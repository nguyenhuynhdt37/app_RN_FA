# StudyNest React Native Skills

This skill set contains custom rules tailored specifically for the architecture of the **StudyNest** project. 

It defines strict guidelines for the AI Agent to follow when writing code, ensuring the output aligns with the project's modern tech stack and complex requirements.

## Core Pillars
1. **AI-Ready UI**: Guidelines for building components that can handle AI streaming and dynamic widget injection without layout shifts (e.g., using Component Slots and Loading Skeletons).
2. **NativeWind (Tailwind v4)**: Strict enforcement of NativeWind for all styling, ensuring dark mode consistency and prohibiting legacy `StyleSheet` usage.
3. **Robust Forms**: Guidelines for using Zod Schemas separated from UI components, and leveraging React Hook Form's Uncontrolled Components to optimize typing performance on mobile devices.
4. **Data Fetching**: Mandatory use of TanStack Query (React Query) for all API interactions to ensure proper caching, background updates, and error handling. No bare `fetch()` inside `useEffect`.
5. **High-Speed Storage**: Mandatory use of `react-native-mmkv` for synchronous, high-performance local storage. `AsyncStorage` is strictly prohibited.
6. **Apple UI Standards**: Strict adherence to iOS design principles including Glassmorphism (`expo-blur`), Spring animations (`react-native-reanimated`), and tactile feedback (`expo-haptics`) to ensure a premium, native feel.
7. **Folder Structure & Feature Slices**: Strict enforcement of a feature-sliced architecture. The `app/` directory is exclusively for Expo routing. Complex logic, components, API calls, and schemas must be organized by feature domain (e.g., `features/auth/`) to ensure long-term maintainability.
