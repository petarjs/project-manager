# App Description:

A lightweight desktop app for macOS that simplifies local project management. Easily create new projects using boilerplate scripts, view and manage existing projects, and launch frontend/backend URLs or open projects in Cursor IDE. Includes a macOS status bar integration for quick access to your project list and tools, with persistent data storage for seamless tracking of ports and Redis configurations. Perfect for developers who want an efficient way to manage and bootstrap local projects.

## **Epic 1: Project Management**

### **Story 1.1: Display List of Projects**

- **Description**: As a user, I want to see a list of all my projects in a table, including project name, port number, and Redis database, so that I can manage them easily.
- **Acceptance Criteria**:
  - ✅ Display project name, port, and Redis DB in a table. (Model and service implemented)
  - ✅ Automatically load data from the ~/projects/personal directory. (Implemented in ProjectService)

### **Story 1.2: Open Project URLs**

- **Description**: As a user, I want to open the frontend (FE) and backend (BE) URLs of a project directly from the list, so I can quickly access the project in a browser.
- **Acceptance Criteria**:
  - ✅ Provide buttons in the table to open FE and BE URLs in the browser.
  - ✅ URLs are based on the project's port number. (Implemented in Project model)

### **Story 1.3: Open Project in Code Editor**

- **Description**: As a user, I want to open a project in Cursor IDE from the app, so I can start coding immediately.
- **Acceptance Criteria**:
  - ✅ Add a button in the table to open the project folder in Cursor IDE.
  - ✅ Use the project's directory path to launch the editor. (Directory path stored in Project model)

### **Story 1.4: Edit Project**

- **Description**: As a user, I want to be able to edit a project, change the port, and change the Redis DB and FE and BE app URLs.
- **Acceptance Criteria**:
  - ✅ Store project configuration (Implemented in Project model and ProjectService)
  - ⏳ UI for editing project details

## **Epic 2: New Project Creation**

### **Story 2.1: Add a New Project**

- **Description**: As a user, I want to create a new project by providing basic details (name and pretty name), so I can set up new projects quickly.
- **Acceptance Criteria**:
  - ✅ Support for APP_NAME and APP_NAME_PRETTY (Implemented in Project model)
  - ✅ Configuration for port number and Redis database number (Implemented in config.py)
  - ✅ Run the provided script with the input values and show live output. (Implemented in ScriptService)

### **Story 2.2: Show Live Script Output**

- **Description**: As a user, I want to see the live output of the project creation script in the app, so I know the progress and if there are any errors.
- **Acceptance Criteria**:
  - ⏳ Display live output from the script in a scrollable text area or popup.
  - ⏳ Handle and display error messages if the script fails.

## **Epic 3: Status Bar Integration**

### **Story 3.1: Add App Icon to macOS Status Bar**

- **Description**: As a user, I want the app to run in the macOS status bar with an icon, so I can access it quickly without opening the full app.
- **Acceptance Criteria**:
  - ✅ Added rumps dependency for status bar support
  - ⏳ Display an app icon in the macOS status bar.
  - ⏳ Show a dropdown menu when clicking the icon.

### **Story 3.2: View Projects from Status Bar**

- **Description**: As a user, I want to see a list of my projects in the status bar dropdown, so I can manage them without opening the full app.
- **Acceptance Criteria**:
  - ⏳ Display project names in the dropdown menu.
  - ⏳ Include submenus or options to open the project in a browser (FE/BE) or Cursor IDE.

### **Story 3.3: Add New Project from Status Bar**

- **Description**: As a user, I want to create a new project directly from the status bar dropdown, so I can quickly start new projects without opening the full app.
- **Acceptance Criteria**:
  - ⏳ Add a "New Project" button in the status bar dropdown.
  - ⏳ Launch the project creation dialog (Tkinter) when the button is clicked.

## **Epic 4: Data Persistence**

### **Story 4.1: Store Project Information**

- **Description**: As a user, I want the app to remember project details (name, port, Redis DB) so I don't have to re-enter them every time I open the app.
- **Acceptance Criteria**:
  - ✅ Store project details in a local file (Implemented JSON storage in ProjectService)
  - ✅ Load the stored details when the app starts (Implemented in ProjectService)

### **Story 4.2: Detect Existing Projects**

- **Description**: As a user, I want the app to automatically detect projects in the ~/projects/personal directory, so I can manage old projects without manual input.
- **Acceptance Criteria**:
  - ✅ Scan the directory for subfolders and load them as projects (Basic implementation in ProjectService)
  - ✅ Populate port and Redis DB fields for existing projects from stored data. (Added auto-assignment with structure detection)

## **Epic 5: User Interface**

### **Story 5.1: Build Main UI**

- **Description**: As a user, I want a clean and simple interface to view and manage my projects, so I can navigate the app easily.
- **Acceptance Criteria**:
  - ⏳ Create a main window with tabs or sections for project list and project creation.
  - ✅ Added Tkinter dependency for UI development

### **Story 5.2: Provide Feedback for User Actions**

- **Description**: As a user, I want visual feedback (popups or notifications) for actions like creating a project or opening a URL, so I know the action was successful.
- **Acceptance Criteria**:
  - ⏳ Show success or error popups after actions like project creation or URL opening.
  - ⏳ Use Tkinter messagebox for notifications.

Legend:
✅ = Completed
⏳ = Pending

edit .env files

Clone the existing project - load the list from github using gh cli - it doesn't need to use gh repo create

Start the fe server in background and show if it's running

When deleting a project, ask to check what you want to delete - directory, database, github repo
