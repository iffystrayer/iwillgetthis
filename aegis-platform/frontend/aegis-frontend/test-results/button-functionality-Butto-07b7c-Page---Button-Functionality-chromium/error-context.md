# Page snapshot

```yaml
- region "Notifications alt+T"
- dialog "Add New User":
  - heading "Add New User" [level=2]:
    - img
    - text: Add New User
  - paragraph: Create a new user account with appropriate roles and permissions.
  - img
  - text: Full Name
  - textbox "Full Name"
  - img
  - text: Email Address
  - textbox "Email Address"
  - img
  - text: Username
  - textbox "Username"
  - img
  - text: Temporary Password
  - textbox "Temporary Password"
  - paragraph: User will be prompted to change password on first login
  - img
  - text: Role & Permissions
  - combobox: Read-Only User View only access
  - text: Read-Only User View only access
  - button "Cancel"
  - button "Create User":
    - img
    - text: Create User
  - button "Close":
    - img
    - text: Close
```