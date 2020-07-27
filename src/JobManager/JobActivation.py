#! /usr/bin/env python

from Job import JobStatus
from MobileExecutor import MExStatus
from JobServiceMethods import call_get_mex_list, call_assign_job, call_change_mex_status

# Job Allocator and Job Refiner.
def job_allocator(pending_jobs_list, active_jobs_list, mexs_list):
    """ 
    Job Allocator method. Check Pending Jobs list and MExs list to assign a Job to a MEx.

    Loops through the Pending Jobs list,
    finds the first pending Job and matches it with an available MEx (Up to date mex_list retrieved from MEx Sentinel service).
    If succesful, it removes this Job from the Pending Jobs list and passes
    it along to the Job Refiner, sends an update to the MEx Sentinel to 
    update the allocated MEx state. If unsuccesful it returns None.
    Should be called/triggered whenever a change is made to either list. 
    """

    
    error_code = 0

    # First query the MEx Sentinal for an up-to-date MExs list.
    mexs_list = call_get_mex_list()

    allocated_job_index = None
    for index, job in enumerate(pending_jobs_list):
        if allocated_job_index != None:
            print("Allocated index: " + str(allocated_job_index))
            break
        elif job.status == JobStatus.PENDING:
            # print("Trying for index: " + str(index))
            # Found a job which is still pending, now find available MEx.
            for mex in mexs_list:
                if mex.status == MExStatus.STANDBY:
                    # Found a MEx which is available (standby)
                    # Check if the job has not got a MEx pre-assigned OR the pre-assigned mex_id matches the MEx's id
                    if (not job.mex_id) or (job.mex_id == mex.id): 
                        mex.status = MExStatus.ASSIGNED
                        mex.job_id = job.id
                        job.assign_mex(mex.id)
                        allocated_job_index = index
                        break
    else:
        # Loop ended without a break
        error_code = 1      # Could not allocate Job to MEx.

    if allocated_job_index != None:
        rough_job = pending_jobs_list.pop(allocated_job_index)  # Removes the allocated job from the Pending Jobs lists.
        call_assign_job(rough_job.id, rough_job.mex_id)         # Send update to MEx Sentinel to update the assigned MEx state.

        return job_refiner(active_jobs_list, mexs_list, rough_job)
    else:
        return error_code     # Failed to allocate any pending jobs.


def job_refiner(active_jobs_list, mexs_list, rough_job):
    """
    Job Refiner method.
    Takes in a rough job and based on the allocated MEx refines the Jobs Tasks to match.
    Starts the Job, sends update to the MEx Sentinel to update the MEx state and 
    then adds the refined Job to the Active Jobs list.
    """
    refined_job = rough_job
    # TODO Refine the Job's tasks based on the rough job's tasks and the assigned MEx.

    refined_job.start_job()
    # Update local copy of MEx Sentinel mex_list (TODO Check: Does this change job_manager mex_list?)
    for mex in mexs_list:
        if mex.id == refined_job.mex_id and mex.job_id == refined_job.id:
            mex.status = MExStatus.EXECUTING_TASK
    
    # Send update to MEx Sentinel to update the started MEx state.
    call_change_mex_status(refined_job.mex_id, MExStatus.EXECUTING_TASK)

    active_jobs_list.append(refined_job)
    return 0    # Return a 0, no errors.