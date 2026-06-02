import asyncio
import logging

from verticals.workflows.retention_cron import retention_cron_webhook

logging.basicConfig(level=logging.INFO)


async def run_test():
    print("====================================")
    print("   Testing Sprint 2.1 Retention Cron")
    print("====================================")
    print("\nSimulating QStash cron trigger (Batch Mode)")

    # We call the batch webhook, which returns a list of coroutines for triggered agents
    tasks = await retention_cron_webhook()

    print(f"\nWebhook triggered {len(tasks)} rescue tasks.")

    if tasks:
        # Await the execution of all triggered agents
        results = await asyncio.gather(*tasks)
        print("\nResults:")
        for idx, result in enumerate(results):
            print(f"Task {idx + 1} Output: {result}")
    else:
        print("\nNo agents were triggered (all clients healthy).")

if __name__ == "__main__":
    asyncio.run(run_test())
