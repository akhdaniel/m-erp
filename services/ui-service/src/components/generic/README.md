# Generic UI Components

This directory contains reusable generic UI components for the XERPIUM system.

## Components

### DateTimePicker

A custom date and datetime picker component with enhanced functionality including:
- Popup calendar for date selection
- Time picker for datetime fields
- Min/max date constraints
- Responsive design
- Keyboard navigation support

#### Usage

```vue
<DateTimePicker
  v-model="selectedDate"
  type="date"
  label="Select a date"
  placeholder="YYYY-MM-DD"
/>
```

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `modelValue` | String/null | Yes | The v-model value |
| `type` | String | Yes | Either 'date' or 'datetime-local' |
| `label` | String | No | Label for the input field |
| `required` | Boolean | No | Whether the field is required |
| `disabled` | Boolean | No | Whether the field is disabled |
| `placeholder` | String | No | Placeholder text for the input |
| `min` | String | No | Minimum allowed date |
| `max` | String | No | Maximum allowed date |
| `help` | String | No | Help text displayed below the input |

#### Integration with Form Schemas

The DateTimePicker is automatically used by the GenericFormView component for fields with type 'date' or 'datetime-local':

```json
{
  "name": "due_date",
  "label": "Due Date",
  "type": "date",
  "required": true
}
```

### Autocomplete

A reusable autocomplete component for selecting from large datasets.

### Other Components

- GenericDashboard
- DashboardWidget
- GenericDetailView
- GenericFormView
- GenericListView

## Testing

Each component should have corresponding unit tests in the `__tests__` directory.

## Documentation

Each component should have a corresponding `.md` documentation file explaining its usage.