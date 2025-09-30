import { mount } from '@vue/test-utils'
import DateTimePicker from '../DateTimePicker.vue'

describe('DateTimePicker', () => {
  it('renders correctly with date type', () => {
    const wrapper = mount(DateTimePicker, {
      props: {
        modelValue: null,
        type: 'date',
        label: 'Test Date'
      }
    })
    
    expect(wrapper.find('label').text()).toBe('Test Date')
    expect(wrapper.find('input').attributes('type')).toBe('date')
  })
  
  it('renders correctly with datetime-local type', () => {
    const wrapper = mount(DateTimePicker, {
      props: {
        modelValue: null,
        type: 'datetime-local',
        label: 'Test DateTime'
      }
    })
    
    expect(wrapper.find('label').text()).toBe('Test DateTime')
    expect(wrapper.find('input').attributes('type')).toBe('datetime-local')
  })
  
  it('emits update:modelValue when input changes', async () => {
    const wrapper = mount(DateTimePicker, {
      props: {
        modelValue: null,
        type: 'date',
        label: 'Test Date'
      }
    })
    
    const input = wrapper.find('input')
    await input.setValue('2025-01-01')
    
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['2025-01-01'])
  })
})