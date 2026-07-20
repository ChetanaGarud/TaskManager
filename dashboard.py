import os
import requests
from datetime import datetime
from shiny import App, ui, render, reactive

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/tasks/")

status_badges = {
    "todo": "bg-secondary",
    "in_progress": "bg-primary",
    "completed": "bg-success"
}

priority_badges = {
    "low": "bg-info text-dark",
    "medium": "bg-warning text-dark",
    "high": "bg-danger"
}

app_ui = ui.page_fluid(
    # Injecting a tiny script to guarantee click delivery regardless of rapid DOM re-renders
    ui.tags.head(
        ui.tags.script("""
            function sendTaskAction(action, taskId) {
                Shiny.setInputValue('global_task_action', {action: action, id: taskId}, {priority: 'event'});
            }
        """)
    ),
    
    ui.panel_title(" Task Manager", "Task Manager"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Create New Task"),
            ui.input_text("task_title", "Task Title", placeholder="Enter task name..."),
            ui.input_text_area("task_desc", "Description", placeholder="Enter context/details..."),
            ui.input_select(
                "task_status", 
                "Initial Status", 
                {"todo": "To Do", "in_progress": "In Progress", "completed": "Completed"}
            ),
            ui.input_select(
                "task_priority",
                "Task Priority",
                {"low": "Low", "medium": "Medium", "high": "High"},
                selected="medium"
            ),
            ui.input_action_button("btn_submit", "Add Task to Workspace", class_="btn-success w-100 mt-2"),
            ui.output_text("form_feedback")
        ),
        
        ui.layout_columns(
            ui.value_box("To Do", ui.output_text("count_todo"), theme="secondary"),
            ui.value_box("In Progress", ui.output_text("count_progress"), theme="primary"),
            ui.value_box("Completed", ui.output_text("count_completed"), theme="success"),
            col_widths=[4, 4, 4],
            class_="mb-4"
        ),
        
        ui.h3("Current Tasks"),
        ui.input_radio_buttons(
            "filter_status", 
            "Filter View:", 
            {"all": "Show All", "todo": "To Do", "in_progress": "In Progress", "completed": "Completed"},
            inline=True
        ),
        ui.hr(),
        ui.output_ui("task_list_display")
    )
)

def server(input, output, session):
    refresh_trigger = reactive.Value(0)
    feedback_message = reactive.Value("")

    @reactive.Calc
    def fetch_current_tasks():
        refresh_trigger.get()
        reactive.invalidate_later(0.5) 
        try:
            response = requests.get(API_URL, timeout=2)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []

    @reactive.Effect
    @reactive.event(input.btn_submit)
    def handle_task_submission():
        title = input.task_title().strip()
        if not title:
            feedback_message.set("⚠️ Title cannot be empty!")
            return

        payload = {
            "title": title, 
            "description": input.task_desc(), 
            "status": input.task_status(),
            "priority": input.task_priority()
        }
        try:
            res = requests.post(API_URL, json=payload, timeout=2)
            if res.status_code in [200, 201]:
                ui.update_text("task_title", value="")
                ui.update_text_area("task_desc", value="")
                feedback_message.set("✓ Task successfully added!")
                refresh_trigger.set(refresh_trigger.get() + 1)
            else:
                feedback_message.set(f"❌ Server rejection: {res.status_code}")
        except requests.exceptions.RequestException:
            feedback_message.set("❌ Connection error: Is backend online?")

    # FIXED: A central, bulletproof observer listening directly to the native JS click events
    @reactive.Effect
    @reactive.event(input.global_task_action)
    def handle_global_task_action():
        action_data = input.global_task_action()
        if not action_data:
            return
            
        action = action_data.get("action")
        t_id = action_data.get("id")
        
        try:
            if action == "delete":
                res = requests.delete(f"{API_URL}{t_id}", timeout=2)
                if res.status_code in [200, 204]:
                    feedback_message.set("✓ Task permanently removed.")
                    refresh_trigger.set(refresh_trigger.get() + 1)
            
            elif action in ["in_progress", "completed", "todo"]:
                res = requests.put(f"{API_URL}{t_id}", json={"status": action}, timeout=2)
                if res.status_code == 200:
                    feedback_message.set(f"✓ Task updated to {action.replace('_', ' ')}.")
                    refresh_trigger.set(refresh_trigger.get() + 1)
        except requests.exceptions.RequestException:
            feedback_message.set("❌ Sync error: Unable to complete action.")

    @output
    @render.text
    def form_feedback():
        return feedback_message.get()

    @output
    @render.text
    def count_todo():
        return str(sum(1 for t in fetch_current_tasks() if (t.get("status") or "todo") == "todo"))

    @output
    @render.text
    def count_progress():
        return str(sum(1 for t in fetch_current_tasks() if t.get("status") == "in_progress"))

    @output
    @render.text
    def count_completed():
        return str(sum(1 for t in fetch_current_tasks() if t.get("status") == "completed"))

    @output
    @render.ui
    def task_list_display():
        tasks = fetch_current_tasks()
        selected_filter = input.filter_status()
        
        ui_elements = []
        for task in tasks:
            status_val = task.get("status") or "todo"
            prio_val = task.get("priority") or "medium"
            t_id = task.get("id")
            
            if selected_filter != "all" and status_val != selected_filter:
                continue

            badge_class = status_badges.get(status_val, "bg-secondary")
            prio_class = priority_badges.get(prio_val, "bg-warning text-dark")
            
            raw_time = task.get("created_at")
            time_str = ""
            if raw_time:
                try:
                    dt = datetime.fromisoformat(raw_time.replace("Z", ""))
                    time_str = dt.strftime("%b %d, %I:%M %p")
                except ValueError:
                    time_str = str(raw_time)[:16]

            # Construct buttons with native HTML click event targets to bypass the reactive refresh block
            action_buttons = []
            if status_val == "todo":
                action_buttons.append(ui.tags.button("In Progress", class_="btn btn-sm btn-outline-primary me-1", onclick=f"sendTaskAction('in_progress', {t_id})"))
                action_buttons.append(ui.tags.button("Done", class_="btn btn-sm btn-outline-success me-1", onclick=f"sendTaskAction('completed', {t_id})"))
            elif status_val == "in_progress":
                action_buttons.append(ui.tags.button("Done", class_="btn btn-sm btn-outline-success me-1", onclick=f"sendTaskAction('completed', {t_id})"))
            elif status_val == "completed":
                action_buttons.append(ui.tags.button("Reopen Task", class_="btn btn-sm btn-outline-secondary me-1", onclick=f"sendTaskAction('todo', {t_id})"))

            action_buttons.append(ui.tags.button("🗑️", class_="btn btn-sm btn-outline-danger", onclick=f"sendTaskAction('delete', {t_id})"))

            card_ui = ui.div(
                ui.div(
                    ui.div(
                        ui.h5(task.get("title", "Untitled Task"), class_="mb-1 card-title"),
                        ui.p(task.get("description", ""), class_="text-muted small mb-1"),
                        ui.div(f"🕒 Created: {time_str}" if time_str else "", class_="text-muted", style="font-size: 0.78rem; font-family: monospace;"),
                        class_="col-md-7"
                    ),
                    ui.div(
                        ui.div(
                            ui.span(status_val.replace("_", " ").title(), class_=f"badge {badge_class} me-1"),
                            ui.span(prio_val.upper(), class_=f"badge {prio_class}"),
                            class_="mb-2"
                        ),
                        ui.div(
                            *action_buttons,
                            class_="d-flex justify-content-end align-items-center"
                        ),
                        class_="col-md-5 text-end"
                    ),
                    class_="row align-items-center p-3 border-bottom"
                ),
                class_="task-item-row"
            )
            ui_elements.append(card_ui)
            
        if not ui_elements:
            return ui.p("No tasks found in this view category.", class_="text-muted italic p-3")
            
        return ui.div(*ui_elements, class_="border rounded bg-white shadow-sm")

app = App(app_ui, server)