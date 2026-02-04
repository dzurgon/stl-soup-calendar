# Optional: a separate runner if you want to run periodic updates outside Flask
from apscheduler.schedulers.blocking import BlockingScheduler
from .app import generate_and_cache

sched = BlockingScheduler()

sched.add_job(generate_and_cache, 'interval', minutes=1440)

if __name__ == '__main__':
    generate_and_cache()
    sched.start()
