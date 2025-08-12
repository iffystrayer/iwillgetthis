# Page snapshot

```yaml
- region "Notifications alt+T"
- dialog "Upload Evidence":
  - heading "Upload Evidence" [level=2]
  - paragraph: Upload compliance evidence and supporting documentation
  - text: File
  - img
  - paragraph: Click to upload or drag and drop
  - paragraph: PDF, Word, Excel, Text, or Image files (max 50MB)
  - button "File"
  - text: Title *
  - textbox "Title *"
  - text: Description
  - textbox "Description"
  - text: Type *
  - combobox: Select evidence type
  - button "Cancel"
  - button "Upload Evidence" [disabled]
  - button "Close":
    - img
    - text: Close
```