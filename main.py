import time
import schedule
from services import WhatsAppService, FlatasticService, StateService, TaskState


def build_completion_message(completed_by: str, task_title: str, next_user: str) -> str:
    """Creates message for completed task."""
    return (f"🧹 *Sauber!* \n'{task_title}' wurde von {completed_by} geputzt.\n\n"
            f"👉 Nächster ist: *{next_user}*")


def build_overdue_message(user: str, title: str, days: int) -> str:
    """Creates message for overdue task."""
    return (f"🚨 *ALARM!* \n@{user}, '{title}' ist seit {days} Tagen überfällig!\n\n"
            f"Bitte sofort erledigen.")


def build_due_message(user: str, title: str) -> str:
    """Creates message for task due today."""
    return (f"📅 *Heute fällig:*\n"
            f"@{user}, bitte putze heute noch das '{title}'.")


def notify_completions(tasks: list, last_state: dict, messenger: WhatsAppService) -> None:
    """Notifies group when tasks are completed."""
    for task in tasks:
        title = task['title']
        current_user = task['user']
        last_user = last_state.get(title)
        
        if last_user and last_user != current_user:
            messenger.send_group_message(
                build_completion_message(last_user, title, current_user)
            )


def notify_reminders(tasks: list, messenger: WhatsAppService) -> None:
    """Sends reminders for due/overdue tasks."""
    for task in tasks:
        state = task['state']
        
        if state == TaskState.OVERDUE:
            messenger.send_group_message(
                build_overdue_message(task['user'], task['title'], abs(task['days_left']))
            )
        elif state == TaskState.DUE:
            messenger.send_group_message(
                build_due_message(task['user'], task['title'])
            )


def run_check(messenger: WhatsAppService | None = None, 
              task_service: FlatasticService | None = None,
              state_service: StateService | None = None) -> None:
    """Main routine check with dependency injection."""
    print("\n--- Starte Routine-Check ---")
    
    messenger = messenger or WhatsAppService()
    task_service = task_service or FlatasticService()
    state_service = state_service or StateService()

    tasks = task_service.get_current_tasks()
    if not tasks:
        print("Keine Aufgaben empfangen (oder Fehler).")
        return

    last_state = state_service.load_state()
    
    notify_completions(tasks, last_state, messenger)
    notify_reminders(tasks, messenger)
    
    state_service.save_state(tasks)
    print("--- Check fertig ---\n")


if __name__ == "__main__":
    run_check()

    schedule.every().day.at("09:00").do(run_check)
    schedule.every().day.at("18:00").do(run_check)
    
    print("🤖 Bot ist aktiv. Drücke Strg+C zum Beenden.")
    while True:
        schedule.run_pending()
        time.sleep(60)
