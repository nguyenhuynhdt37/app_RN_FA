# Form Validation: Zod Schemas

When handling user inputs, quizzes, or complex forms, validation logic must be robust, type-safe, and independent of the rendering cycle.

## The Rule

1. **Always use `zod`** for defining data validation schemas.
2. **Decouple the Zod Schema from the React Component.** Define the schema outside the component or in a separate file (e.g., `schema.ts`) so it can be reused across the frontend and backend/API boundaries.
3. Extract TypeScript types directly from the Zod schema using `z.infer<typeof Schema>`.

### Do

```tsx
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

// 1. Define schema outside the component
export const quizAnswerSchema = z.object({
  questionId: z.string().uuid(),
  answerText: z.string().min(1, 'Answer cannot be empty').max(500),
});

// 2. Extract Type
export type QuizAnswerFormValues = z.infer<typeof quizAnswerSchema>;

export function QuizForm() {
  const { control, handleSubmit, formState: { errors } } = useForm<QuizAnswerFormValues>({
    resolver: zodResolver(quizAnswerSchema),
  });

  const onSubmit = (data: QuizAnswerFormValues) => {
    // Type-safe data
    console.log(data.answerText);
  };

  // ... render form
}
```

### Don't

```tsx
import { useState } from 'react';

export function QuizForm() {
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');

  const onSubmit = () => {
    // Ad-hoc validation inside the component
    if (!answer) {
      setError('Answer cannot be empty');
      return;
    }
    if (answer.length > 500) {
      setError('Answer too long');
      return;
    }
    // Hard to reuse this logic or share types
  };
  
  // ... render form
}
```
