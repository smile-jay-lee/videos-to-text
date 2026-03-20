/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  corePlugins: { preflight: false }, // 保留现有全局 CSS，不让 Tailwind Reset 覆盖
  theme: { extend: {} },
  plugins: [],
}
