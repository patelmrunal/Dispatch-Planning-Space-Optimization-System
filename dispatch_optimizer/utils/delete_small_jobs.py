from dispatch_optimizer.utils.job_db import list_jobs, get_job_by_id, delete_job_by_id
import pandas as pd
import io

def main():
    jobs = list_jobs()
    deleted = 0
    for j in jobs:
        job = get_job_by_id(j[0])
        if job and job[2]:
            try:
                n = len(pd.read_csv(io.StringIO(job[2])))
            except Exception as e:
                n = 0
            if n < 50:
                delete_job_by_id(j[0])
                deleted += 1
                print(f'Deleted job {j[0]} with {n} products')
    print(f'Total deleted: {deleted}')

if __name__ == '__main__':
    main() 