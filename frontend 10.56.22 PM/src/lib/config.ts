export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  useMocks: process.env.NEXT_PUBLIC_USE_MOCKS === "true",
};