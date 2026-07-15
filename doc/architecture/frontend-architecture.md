# Frontend Architecture

## Stack

- Vite
- Vue 3
- TypeScript
- Composition API with script setup
- Vue Router
- Pinia
- Tailwind CSS
- daisyUI

## Structure

    frontend/
      src/
        api/
          client.ts
          generated/
          modules/
        assets/
          main.css
        components/
          layout/
          feedback/
          settings/
        composables/
        router/
        stores/
        types/
        utils/
        views/
      vite.config.ts
      package.json

## Responsibilities

Frontend รับผิดชอบ presentation, input UX, navigation และ client-side feedback เท่านั้น

Frontend ห้ามตัดสิน:

- Permission และ organization scope
- ว่าหมดเวลาจริงหรือไม่
- คะแนนและความถูกต้อง
- Personnel reconciliation
- Exam lifecycle transition

## Composition API Convention

- ทุก Single File Component ใช้ script setup lang="ts"
- Component props/events มี TypeScript types
- Reusable behavior อยู่ใน composable
- View orchestration ไม่ควรอัด logic ทั้งหมดใน component เดียว
- Component และ composable อยู่ภายใต้ 800-line limit

## Container Component Convention

Use the following page composition as the default:

    App.vue (application shell and global initialization)
      PageContainer (width, spacing, responsive padding)
        PageHeader (title, description, page actions)
          page/container view (API, composables, route and state orchestration)
            presentational components (props in, events out)

Page/container views may coordinate API modules, local state, composables, and selected Pinia stores. They must not duplicate global layout or embed large reusable UI blocks. Presentational components must remain API-agnostic and business-rule-agnostic.

## Feedback and Theme

- Use daisyUI-first reusable components for alerts, toasts, and confirmation dialogs.
- Do not call browser `window.alert`, `window.confirm`, or `window.prompt`.
- Themes are daisyUI themes applied through `document.documentElement.dataset.theme`.
- `stores/theme.ts` is the single client-side owner of the selected theme; persistence uses localStorage only.
- Add a Pinia store only when state is shared across pages or represents a global UI concern.

## State Decision

| Scope | Mechanism | Examples |
|---|---|---|
| Component เดียว | ref/reactive/computed | dialog, loading, form error |
| Logic ใช้ซ้ำ | composable | timer, pagination, API error |
| ข้ามหลายหน้า | Pinia | current user, active exam session |
| Durable/authoritative | API/database | answers, score, permissions |

Pinia stores ที่อนุมัติเป็น baseline:

- auth store: current user, permissions, active organization scope
- exam session store: session ID, status, endsAt, questions, saved answer view

ห้ามสร้าง global store สำหรับ modal, page filter หรือ temporary form ที่ใช้หน้าเดียว

## API Client

- Base URL มาจาก VITE_API_BASE_URL
- มี client กลางหนึ่งตัว
- Error mapping ใช้ server error code
- ห้าม call fetch กระจายโดยไม่มี module wrapper
- TypeScript API types generate จาก OpenAPI เมื่อ pipeline พร้อม
- Generated files ห้ามแก้ด้วยมือ

## Exam Timer

- รับ server_time และ ends_at
- คำนวณ offset เพื่อแสดง countdown
- Timer เป็น UI hint ไม่เป็น authority
- เมื่อถึงศูนย์ UI เรียก finalize/refresh แต่ Backend ตรวจเวลาอีกครั้ง

## Styling

src/assets/main.css:

    @import "tailwindcss";
    @plugin "daisyui";

- ใช้ daisyUI components ก่อนสร้าง design system เพิ่ม
- Theme และ accessibility token อยู่จุดเดียว
- หลีกเลี่ยง style ซ้ำในหลาย component

## Routing

- Route meta ระบุ authentication/role เพื่อ UX
- Backend ยังต้องตรวจ permission ทุก request
- Lazy-load route views เมื่อคุ้มค่า
- SPA fallback ต้องตั้งค่าใน hosting

## Testing

- Unit test composables/stores ที่มี logic
- Component test เฉพาะ interaction สำคัญ
- API business rules ทดสอบหลักด้วย pytest
- E2E เริ่มจาก smoke flows ที่เสี่ยงสูงเมื่อมี phase hardening

## Build

- package-lock.json ต้อง commit
- Development ใช้ Vite
- Production ใช้ static files จาก vite build
- Node.js ไม่ต้องอยู่ใน runtime container หลัง build
