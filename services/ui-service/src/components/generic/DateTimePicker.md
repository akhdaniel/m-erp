# DateTimePicker Component Documentation

The DateTimePicker component is a custom Vue component that provides enhanced date and datetime selection capabilities for forms in the XERPIUM system.

## Features

- Supports both date and datetime-local input types
- Includes a popup calendar for easy date selection
- Time picker for datetime fields
- Responsive design that works on all screen sizes
- Keyboard navigation support
- Min/max date constraints
- Accessible with proper labeling and ARIA attributes

## Usage

### Basic Usage

```vue
<DateTimePicker
  v-model="selectedDate"
  type="date"
  label="Select a date"
  placeholder="YYYY-MM-DD"
/>
```

### DateTime Selection

```vue
<DateTimePicker
  v-model="selectedDateTime"
  type="datetime-local"
  label="Select date and time"
  placeholder="YYYY-MM-DDTHH:mm"
/>
```

### With Constraints

```vue
<DateTimePicker
  v-model="selectedDate"
  type="date"
  label="Select a date"
  :min="minDate"
  :max="maxDate"
  required
  help="Please select a date between the allowed range"
/>
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `modelValue` | String/null | Yes | The v-model value (date/datetime string or null) |
| `type` | String | Yes | Either 'date' or 'datetime-local' |
| `label` | String | No | Label for the input field |
| `required` | Boolean | No | Whether the field is required |
| `disabled` | Boolean | No | Whether the field is disabled |
| `placeholder` | String | No | Placeholder text for the input |
| `min` | String | No | Minimum allowed date (YYYY-MM-DD format) |
| `max` | String | No | Maximum allowed date (YYYY-MM-DD format) |
| `help` | String | No | Help text displayed below the input |

## Events

The component emits the standard `update:modelValue` event when the value changes.

## Integration with Form Schemas

To use the DateTimePicker in form schemas (UI schemas), simply specify the field type as either 'date' or 'datetime-local':

```json
{
  "name": "due_date",
  "label": "Due Date",
  "type": "date",
  "required": true,
  "placeholder": "Select a date"
}
```

The GenericFormView component automatically uses the DateTimePicker component for these field types.

## Examples

See `/test/datetime` route in the application for a working example of the DateTimePicker component.

## Styling

The component uses Tailwind CSS classes and follows the XERPIUM design system. It integrates seamlessly with other form components.

## Accessibility

The component includes:
- Proper labeling with `for`/`id` associations
- Keyboard navigation support
- Focus management
- ARIA attributes where appropriate
- Screen reader friendly markup