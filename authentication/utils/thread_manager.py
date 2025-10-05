from concurrent.futures import ThreadPoolExecutor, as_completed

class ThreadManager:
    def __init__(self, max_workers=10):
        """
        Initialize the ThreadManager with a configurable number of workers.

        :param max_workers: Maximum number of threads to use in the pool.
        """
        self.max_workers = max_workers

    def execute(self, tasks):
        """
        Execute a list of tasks using a ThreadPoolExecutor.

        :param tasks: List of tuples where each tuple contains:
                      (function, *args, **kwargs)
        :return: List of results. If a task fails, it appends an error dictionary.
        """
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(task[0], *task[1], **task[2]) if len(task) > 2
                else executor.submit(task[0], *task[1]) for task in tasks
            ]

            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "details": "Failed to process task."
                    })
        return results

if __name__ == "__main__":
    """
    Example usage of ThreadManager to create notifications for all active users.

    from django.contrib.auth.models import User
    from notifications.utils import create_notification
    from path.to.thread_manager import ThreadManager  # Adjust the import as needed

    # Get all active users
    users = User.objects.filter(is_active=True)

    # Prepare the list of tasks
    tasks = []
    for user in users:
        tasks.append((
            create_notification,           # Function to call
            (user, "This is a threaded notification!", "/notifications/"),  # args
            {}                              # kwargs (empty)
        ))

    # Initialize the ThreadManager with 5 workers
    manager = ThreadManager(max_workers=5)

    # Execute all tasks concurrently
    results = manager.execute(tasks)

    print(results)  # Output the results
    """
    pass  # No actual execution when imported as a module