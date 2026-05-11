# Form Performance: Uncontrolled Components

In React Native, especially on lower-end devices or when dealing with long forms (like quizzes or essay inputs), binding text inputs to React state (`useState`) can cause significant typing lag due to frequent re-renders on every keystroke.

## The Rule

1. **Avoid using `useState` to store the value of a `<TextInput>`** if the component is complex.
2. **Use React Hook Form (`useForm`) with uncontrolled components.** Use the `<Controller>` component provided by React Hook Form. This registers the input without causing the entire parent form to re-render on every keystroke.
3. If you do not use React Hook Form, use a `useRef` to store the input value if you only need the value on submit.

### Do

```tsx
import { View, TextInput, Button, Text } from 'react-native';
import { useForm, Controller } from 'react-hook-form';

export function UncontrolledEssayForm() {
  const { control, handleSubmit } = useForm();

  const onSubmit = (data: any) => {
    console.log(data.essay);
  };

  return (
    <View className="flex-1 p-4">
      {/* 
        Controller manages the value internally. 
        Typing does not trigger a re-render of UncontrolledEssayForm.
      */}
      <Controller
        control={control}
        name="essay"
        defaultValue=""
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            className="p-4 border border-zinc-300 rounded-lg dark:border-zinc-700 dark:text-white"
            multiline
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
          />
        )}
      />
      <Button title="Submit" onPress={handleSubmit(onSubmit)} />
    </View>
  );
}
```

### Don't

```tsx
import { useState } from 'react';
import { View, TextInput, Button } from 'react-native';

export function ControlledEssayForm() {
  const [essay, setEssay] = useState('');

  // Every single keystroke forces React to re-render the entire ControlledEssayForm.
  // On an old Android phone, fast typing will lag severely.
  return (
    <View className="flex-1 p-4">
      <TextInput
        className="p-4 border border-zinc-300 rounded-lg"
        multiline
        value={essay}
        onChangeText={setEssay} 
      />
      <Button title="Submit" onPress={() => console.log(essay)} />
    </View>
  );
}
```
