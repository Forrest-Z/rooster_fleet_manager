#! /usr/bin/env python

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
from std_msgs.msg import UInt8

class TaskType:
    """Class that acts as an enum for the different kinds of tasks."""
    ROBOTMOVEBASE = 0
    AWAITINGLOADCOMPLETION = 1

class TaskStatus:
    """ Class that acts as Enumerator for Task status. """
    # 0 = PENDING, 1 = ACTIVE, 2 = CANCELLED, 3 = SUCCEEDED, 4 = ABORTED
    PENDING = 0
    ACTIVE = 1
    CANCELLED = 2
    SUCCEEDED = 3
    ABORTED = 4
    

class RobotMoveBase:
    """
    Task class: RobotMobeBase, implements move_base action calls to robot navigation stack.
    Used by the higher level Job class to populate a list with its job tasks.
    """
    def __init__(self, location):
        self.id = None                      # ID of the robot to perform the move_base on
        self.location = location            # location of the goal of the move_base.
        self.type = TaskType.ROBOTMOVEBASE  # Task type.

    #region Callback definitions
    def active_cb(self):
        """
        Callback for starting move_base action.
        Connected to actionlib send_goal call.
        """
        rospy.loginfo(self.id + ". Goal pose being processed")

    def feedback_cb(self, feedback):
        """
        Callback for continuous feedback of move_base position.
        Connected to actionlib send_goal call.
        """
        pass    # Don't spam the console for now..
        # rospy.loginfo("Current location: "+str(feedback))

    def done_cb(self, status, result):
        """
        Callback for stopping of goal.
        Connected to actionlib send_goal call.
        move_base callback status options: PENDING=0, ACTIVE=1, PREEMPTED=2, SUCCEEDED=3,
        ABORTED=4, REJECTED=5, PREEMPTING=6, RECALLING=7, RECALLED=8, LOST=9.
        """
        callback_status = None
        if status == 3:
            callback_status = TaskStatus.SUCCEEDED
            rospy.loginfo(self.id + ". Goal reached")
        if status == 2 or status == 8:
            callback_status = TaskStatus.CANCELLED
            rospy.loginfo(self.id + ". Goal cancelled")
        if status == 4:
            callback_status = TaskStatus.ABORTED
            rospy.loginfo(self.id + ". Goal aborted")
        
        if self.job_callback:
            self.job_callback([self.task_id, callback_status])
    #endregion

    def start(self, robot_id, task_id, job_callback):
        """
        Start the task's specific action.
        All job tasks should have this method: 'start', with these
        arguments: 'self', 'robot_id', 'task_id', 'job_callback'.
        """
        self.id = robot_id
        self.task_id = task_id
        self.job_callback = job_callback
        self.move_robot()

    def move_robot(self):
        """ Start a move_base action using actionlib. """
        self.navclient = actionlib.SimpleActionClient(self.id + '/move_base',MoveBaseAction)
        self.navclient.wait_for_server()

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        goal.target_pose.pose.position.x = self.location.x
        goal.target_pose.pose.position.y = self.location.y
        goal.target_pose.pose.position.z = 0.0
        quaternion = quaternion_from_euler(0, 0, self.location.theta)
        goal.target_pose.pose.orientation.x = quaternion[0]
        goal.target_pose.pose.orientation.y = quaternion[1]
        goal.target_pose.pose.orientation.z = quaternion[2]
        goal.target_pose.pose.orientation.w = quaternion[3]

        self.navclient.send_goal(goal, done_cb=self.done_cb, active_cb=self.active_cb, feedback_cb=self.feedback_cb)
    
    def get_status(self):
        """ Retrieve the status of the move_base action. """
        if self.navclient:
            return self.navclient.get_state()
        else:
            return None     # Return None if the navclient was not initialized yet.

class AwaitingLoadCompletion:
    """
    Task class: AwaitingLoadCompletion, waits for input from user or system to mark loading of the robot as succeeded, cancelled, aborted.
    Used by the higher level Job class to populate a list with its job tasks.
    """
    def __init__(self):
        self.id = None                                  # ID of the robot awaiting loading.
        self.status = TaskStatus.PENDING                # PENDING, ACTIVE, CANCELLED, SUCCEEDED, ABORTED
        self.type = TaskType.AWAITINGLOADCOMPLETION     # Task type

    def start(self, robot_id, task_id, job_callback):
        """
        Start the task's specific action.
        All job tasks should have this method: 'start', with these
        arguments: 'self', 'robot_id', 'task_id', 'job_callback'.
        """
        self.id = robot_id
        self.task_id = task_id
        self.job_callback = job_callback
        self.status = TaskStatus.ACTIVE
        self.input_subcriber = rospy.Subscriber(self.id + "/LoadInput", UInt8, self.input_cb)	# Subscribe to /'robot_id'/LoadInput topic to listen for published user/system input.
        rospy.loginfo(self.id + ". Awaiting load completion input...")
    
    def input_cb(self, data):
        """
        Callback method for any user or system input.
        Updates the instance status and calls the higher level job_callback.
        load status option: PENDING=0 ACTIVE=1, CANCELLED=2, SUCCEEDED=3,
        ABORTED=4.
        """
        if self.job_callback:      # Only process callback if this task was started.
            # Input received from user/system,
            if data.data == 3:
                # Loading was completed succesfully.
                self.status = TaskStatus.SUCCEEDED
            elif data.data == 2:
                # Loading was cancelled by user.
                self.status = TaskStatus.CANCELLED
            elif data.data == 4:
                # Loading encountered an error and had to abort.
                self.status = TaskStatus.ABORTED
            
            if data.data == 2 or data.data == 3 or data.data == 4:   # User input meaning some kind of end: cancel, succes or abort.
                self.input_subcriber.unregister()   # Unsubscribe to topic, as this task of the job is done.

            self.job_callback([self.task_id, self.status])     # Call the higher level Job callback.
    
    def get_status(self):
        """ Retrieve the status of the 'AwaitingLoadCompletion'  task. """
        return self.status