import { defineStore } from "pinia";
import { ref } from "vue";

export const DAISYUI_THEMES = [
  "light",
  "dark",
  "cupcake",
  "bumblebee",
  "emerald",
  "corporate",
  "synthwave",
  "retro",
  "cyberpunk",
  "valentine",
  "halloween",
  "garden",
  "forest",
  "aqua",
  "lofi",
  "pastel",
  "fantasy",
  "wireframe",
  "black",
  "luxury",
  "dracula",
  "cmyk",
  "autumn",
  "business",
  "acid",
  "lemonade",
  "night",
  "coffee",
  "winter",
  "dim",
  "nord",
  "sunset",
  "caramellatte",
  "abyss",
  "silk",
] as const;

export type DaisyTheme = (typeof DAISYUI_THEMES)[number];

const THEME_STORAGE_KEY = "mtexam.theme";

function readStoredTheme(): DaisyTheme {
  if (typeof window === "undefined") return "light";
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
  return DAISYUI_THEMES.includes(stored as DaisyTheme) ? (stored as DaisyTheme) : "light";
}

export const useThemeStore = defineStore("theme", () => {
  const theme = ref<DaisyTheme>(readStoredTheme());

  function applyTheme(): void {
    if (typeof document !== "undefined") {
      document.documentElement.dataset.theme = theme.value;
    }
  }

  function initialize(): void {
    theme.value = readStoredTheme();
    applyTheme();
  }

  function setTheme(nextTheme: DaisyTheme): void {
    theme.value = nextTheme;
    if (typeof window !== "undefined") {
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    }
    applyTheme();
  }

  return { theme, initialize, setTheme };
});
