# Page snapshot

```yaml
- region "Notifications alt+T"
- dialog "Create New Task":
  - heading "Create New Task" [level=2]
  - paragraph: Create a new security or compliance task. Fill in the details below to get started.
  - text: Task Title *
  - textbox "Task Title *"
  - text: Description
  - textbox "Description"
  - text: Priority *
  - combobox: Select priority
  - text: Task Type
  - combobox: Select type
  - text: Assigned To
  - textbox "Assigned To"
  - text: Due Date
  - button "Select due date":
    - img
    - text: Select due date
  - text: Category
  - textbox "Category"
  - button "Cancel"
  - button "Create Task"
  - button "Close":
    - img
    - text: Close
```