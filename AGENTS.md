# Airgun - AI Agent Guide

**Project**: SatelliteQE Airgun  
**Repository**: https://github.com/SatelliteQE/airgun

---
### Quick Developer Reference
- **Before committing, run the Pre-commit Hooks**
    - Run manually: `pre-commit run --all-files`

- **Follow conventional commit format when naming commits**

- **For local testing, run a local install within your robottelo folder**
    - Within the robottelo directory: `pip install <path to airgun directory>` 

---
### Purpose
- Separates UI element definitions (**Views**) from webpage interactions (**Entities**)
- Uses Selenium for navigation
- Supports **PatternFly 4** and **PatternFly 5** UI components

### Key Technologies
- **Selenium**: Browser automation
- **Widgetastic**: Widget abstraction layer
- **navmazing**: Declarative navigation system
- **pytest**: Test framework integration

---

## Architecture

Airgun follows a **three-layer architecture** that separates concerns and makes UI testing more maintainable:

### Layer 1: Test Layer
The top layer where tests are written. Tests use the **Session** object to interact with the Satellite UI without needing to know implementation details.

- **Purpose**: Write test logic using high-level entity methods
- **Example**: `session.activationkey.create({'name': 'my-key'})`
- **Benefits**: Tests are clean, readable, and maintainable

### Layer 2: Entity Layer
The middle layer containing pytest functions that interact with webpages.

- **Purpose**: Provide reusable methods for UI interactions
- **Location**: `airgun/entities/` (e.g., `activationkey.py`, `host.py`)
- **Responsibilities**:
  - Navigate to appropriate pages
  - Fill forms and click buttons via views
  - Handle flash messages and errors
  - Return structured data from pages

### Layer 3: View Layer
The bottom layer defining UI element structures using Widgetastic widgets. Views map to actual pages or components in the Satellite UI.

- **Purpose**: Define where elements are located on pages
- **Location**: `airgun/views/` (e.g., `activationkey.py`, `host.py`)
- **Responsibilities**:
  - Define widget locators (XPath, ID, CSS)
  - Verify page display with `is_displayed` property

### Component Relationships

- **Entity** (`entities/`): Pytest functions that use navigation and views to interact with webpages
- **View** (`views/`): UI element definitions using Widgetastic widgets with locators

---

## Key Concepts

### 1. **Entities**

Entities provide **business logic** methods (Sometimes CRUD operations, sometimes entity specific operations, usually both):

```python
class ActivationKeyEntity(BaseEntity):
    def create(self, values):
        """Create a new activation key"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
    
    def read(self, entity_name):
        """Read activation key details"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()
```

**Location**: `airgun/entities/<feature>.py`

### 2. **Views**

Views define **UI element structure** using Widgetastic widgets:

```python
class ActivationKeyCreateView(BaseLoggedInView):
    name = TextInput(id='name')
    description = TextInput(id='description')
    submit = Button('Submit')
    
    @property
    def is_displayed(self):
        return self.name.is_displayed and self.browser.title == 'New Activation Key'
```

**Location**: `airgun/views/<feature>.py`

### 3. **Widgets**

Reusable UI components defined in `widgets.py`:

```python
from airgun.widgets import SatTable, Search, LCESelector

class MyView(BaseLoggedInView):
    searchbox = Search()
    table = SatTable(locator='//table[@id="my-table"]')
    lce_selector = LCESelector()
```

**Common Widgets**:
- `SatTable`: Satellite-specific table widget
- `Search`: Search bar with autocomplete
- `LCESelector`: Lifecycle Environment selector
- `ContextSelector`: Organization/Location switcher
- `SatFlashMessages`: Flash message handler

### 4. **Navigation**

Navigation is **declarative** using navmazing:

```python
from airgun.navigation import NavigateStep, navigator

@navigator.register(ActivationKeyEntity, 'All')
class ShowAllActivationKeys(NavigateStep):
    VIEW = ActivationKeysView
    
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Activation Keys')

@navigator.register(ActivationKeyEntity, 'New')
class CreateNewActivationKey(NavigateStep):
    VIEW = ActivationKeyCreateView
    prerequisite = NavigateToSibling('All')
    
    def step(self, *args, **kwargs):
        self.parent.new.click()
```

**Key Points**:
- `VIEW`: The view class to instantiate
- `prerequisite`: Navigation dependencies
- `step()`: Actions to reach this page

---

## Code Standards

### Import Ordering

1. **Standard library** imports
2. **Third-party** imports (alphabetical)
3. **Airgun** imports (alphabetical)
4. Blank line between groups

```python
# Standard library
import logging
from datetime import datetime

# Third-party
from widgetastic.widget import Text, TextInput, View
from widgetastic_patternfly5 import Button, Table

# Airgun
from airgun.entities.base import BaseEntity
from airgun.views.common import BaseLoggedInView
from airgun.widgets import Search, SatTable
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| **Classes** | PascalCase | `ActivationKeyEntity`, `HostCreateView` |
| **Functions/Methods** | snake_case | `create()`, `read()`, `navigate_to()` |
| **Constants** | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT`, `MAX_RETRIES` |
| **Private** | Leading underscore | `_helper`, `_navigate()` |
| **View Classes** | End with "View" | `ActivationKeyCreateView` |
| **Entity Classes** | End with "Entity" | `ActivationKeyEntity` |

## Common Patterns

### Pattern 1: Basic Entity Actions

```python
class MyEntity(BaseEntity):
    def search(self, query):
        """Search for entities"""
        view = self.navigate_to(self, 'All')
        view.searchbox.search(query)
        return view.table.read()
    
    def read(self, entity_name):
        """Read entity details"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()
    
```

### Pattern 2: Searchable View

```python
class MyListView(BaseLoggedInView):
    title = Text('.//h1')
    searchbox = Search()
    new = Button('Create')
    table = SatTable(locator='//table[@aria-label="my-table"]')
    
    @property
    def is_displayed(self):
        return self.title.is_displayed
```

### Pattern 3: Tab page views

```python
class MyTabsListView(View):

    @View.nested
    class details_tab(PF5Tab):
        TAB_NAME = 'details'
        name = TextInput(id='name')

    @View.nested
    class content_tab(PF5Tab):
        TAB_NAME = 'content'
        table = SatTable(locator='//table')
```

---

## Widget System

### Locator Strategies

```python
# XPath (most common)
Text('.//span[@class="status"]')

# ID
TextInput(id='username')

# CSS Selector
Button(locator='css:button.primary')

# Parametrized Locator
ParametrizedLocator('.//div[@data-id={@item_id}]')
```

---

## Navigation System

### Navigation Registration

```python
@navigator.register(MyEntity, 'All')
class NavigateToAll(NavigateStep):
    VIEW = MyListView
    
    def step(self):
        self.view.menu.select('My Menu', 'Submenu')

@navigator.register(MyEntity, 'Edit')
class NavigateToEdit(NavigateStep):
    VIEW = MyEditView
    prerequisite = NavigateToSibling('All')
    
    def step(self, entity_name):
        # entity_name passed from navigate_to() call
        self.parent.searchbox.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
```

### Using Navigation

```python
# In entity methods
view = self.navigate_to(self, 'All')
view = self.navigate_to(self, 'Edit', entity_name='my-entity')

# Check current location
if self.navigate_to(self, 'All', _is_displayed_check=True):
    # Already on the page
    pass
```

---

## Best Practices

### DO ✅

- **Use `BaseLoggedInView`** for all Satellite pages
- **Wait for elements** before interacting
- **Use descriptive variable names**
- **Add docstrings** to public methods
- **Keep views and entities separate**
- **Prioritize readability over complexity**
- **Write flat code structures over nested code structures**
- **Use Patternfly5 when generating views/entities**
- **Add newly created entities to the import list in airgun/session.py and as a cached property in the Session class**
- **When importing from OUIA, follow this pattern**:
    widgetastic.patternfly5.ouia import (
        Button as PF5OUIAButton
    )
- **When importing from the PF5 library, follow this pattern**:
    widgetastic.patternfly5 import (
        Button as PF5Button
    )

### DON'T ❌

- **Don't use hard-coded sleeps** (`time.sleep()`) - use `wait_for` instead
- **Don't create circular imports** between view files
- **Don't put business logic in views** - keep it in entities
- **Don't use absolute XPaths** - use relative or attributes
- **Don't duplicate widgets** - create reusable components in `widgets.py`
- **Don't generate new entities unless asked for specifically**
- **Don't generate navigators automatically** - only create when asked
- **Don't use OUIA-Generated IDs** - they're unstable and change between renders. Use stable attributes instead:
  - ✅ Class names: `pf-v5-c-table`, `pf-v5-c-menu`
  - ✅ ARIA labels: `aria-label="Kebab toggle"`
  - ✅ Data attributes: `data-label="CVE ID"`
  - ✅ Element types: `//select`, `//button`
  - ❌ `data-ouia-component-id="OUIA-Generated-FormSelect-default-3"`
- **Don't use negative indexing for table columns** - Widgetastic doesn't support `row[-1]`. Use column header text as keys instead: `row['Column with row actions']`
- **Don't override ROOT in table column widgets** unless necessary - the table infrastructure handles finding the `<td>` element

---

## Additional Resources

- **Documentation**: https://airgun.readthedocs.io/
- **Widgetastic Docs**: https://widgetastic.readthedocs.io/
- **navmazing Docs**: https://navmazing.readthedocs.io/
- **Repository**: https://github.com/SatelliteQE/airgun
- **Issues**: https://github.com/SatelliteQE/airgun/issues
- **Selenium Docs**: https://www.selenium.dev/documentation/
- **Widgetastic Docs**: https://widgetastic.readthedocs.io/en/latest/
- 
---

**Last Updated**: 2025-11-11  
**Maintainers**: Sam Bible, Cole Higgins
