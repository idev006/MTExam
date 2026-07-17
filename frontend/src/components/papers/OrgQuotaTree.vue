<script setup lang="ts">
import { computed, ref, watch } from "vue";
import {
  descendantCount,
  findSelectedAncestor,
  hasSelectedDescendant,
  sortOrgUnitsByName,
  type QuotaOrgUnit,
} from "@/components/papers/orgQuota";

const props = defineProps<{
  units: QuotaOrgUnit[];
  selectedIds: string[];
  quotaCounts: Record<string, number>;
}>();

const emit = defineEmits<{
  toggle: [id: string, checked: boolean];
  updateQuota: [id: string, count: number];
}>();

const expandedIds = ref<Set<string>>(new Set());
const byId = computed(() => new Map(props.units.map((unit) => [unit.id, unit])));
const childrenByParent = computed(() => {
  const result = new Map<string, QuotaOrgUnit[]>();
  for (const unit of props.units) {
    if (!unit.parent_id || !byId.value.has(unit.parent_id)) continue;
    result.set(unit.parent_id, [...(result.get(unit.parent_id) ?? []), unit]);
  }
  for (const [parentId, children] of result) result.set(parentId, sortOrgUnitsByName(children));
  return result;
});
const roots = computed(() => sortOrgUnitsByName(props.units.filter(
  (unit) => !unit.parent_id || !byId.value.has(unit.parent_id),
)));
const visibleRows = computed(() => {
  const rows: Array<{ unit: QuotaOrgUnit; depth: number }> = [];
  const visit = (unit: QuotaOrgUnit, depth: number) => {
    rows.push({ unit, depth });
    if (!expandedIds.value.has(unit.id)) return;
    for (const child of childrenByParent.value.get(unit.id) ?? []) visit(child, depth + 1);
  };
  for (const root of roots.value) visit(root, 0);
  return rows;
});
const selectedUnits = computed(() => props.selectedIds
  .map((id) => byId.value.get(id))
  .filter((unit): unit is QuotaOrgUnit => Boolean(unit)));

watch(roots, (rows) => {
  const next = new Set(expandedIds.value);
  for (const row of rows) next.add(row.id);
  expandedIds.value = next;
}, { immediate: true });

function childrenOf(id: string): QuotaOrgUnit[] {
  return childrenByParent.value.get(id) ?? [];
}

function toggleExpanded(id: string) {
  const next = new Set(expandedIds.value);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  expandedIds.value = next;
}

function isSelected(id: string): boolean {
  return props.selectedIds.includes(id);
}

function selectedAncestor(unit: QuotaOrgUnit): QuotaOrgUnit | null {
  return findSelectedAncestor(props.units, props.selectedIds, unit.id);
}

function blockedByDescendant(unit: QuotaOrgUnit): boolean {
  return hasSelectedDescendant(props.units, props.selectedIds, unit.id);
}

function isDisabled(unit: QuotaOrgUnit): boolean {
  return !isSelected(unit.id) && (Boolean(selectedAncestor(unit)) || blockedByDescendant(unit));
}

function levelLabel(level: string): string {
  return ({ division: "กองบัญชาการ", bureau: "กองบังคับการ", station: "สถานี", sub_unit: "ฝ่าย/งาน" } as Record<string, string>)[level] ?? level;
}

function updateQuota(id: string, event: Event) {
  emit("updateQuota", id, Number((event.target as HTMLInputElement).value));
}
</script>

<template>
  <div data-testid="org-quota-tree" class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_20rem]">
    <div class="overflow-hidden rounded-box border border-base-300 bg-base-100">
      <div class="border-b border-base-300 bg-base-200/60 px-4 py-3">
        <p class="font-semibold">โครงสร้างหน่วยงาน</p>
        <p class="text-xs text-base-content/60">เลือกได้หลายหน่วยเมื่อไม่ใช่หน่วยแม่–ลูกในสายเดียวกัน</p>
      </div>
      <div class="max-h-[32rem] divide-y divide-base-300 overflow-y-auto">
        <div
          v-for="row in visibleRows"
          :key="row.unit.id"
          class="px-3 py-3 transition-colors"
          :class="isSelected(row.unit.id) ? 'bg-primary/5' : ''"
        >
          <div class="flex min-w-0 items-start gap-2" :style="{ paddingInlineStart: `${row.depth * 1.25}rem` }">
            <button
              v-if="childrenOf(row.unit.id).length"
              class="btn btn-square btn-ghost btn-xs mt-0.5 shrink-0"
              type="button"
              :aria-label="`${expandedIds.has(row.unit.id) ? 'ย่อ' : 'ขยาย'} ${row.unit.name}`"
              :aria-expanded="expandedIds.has(row.unit.id)"
              @click="toggleExpanded(row.unit.id)"
            >
              <span :class="expandedIds.has(row.unit.id) ? 'rotate-90' : ''" class="transition-transform">▶</span>
            </button>
            <span v-else class="w-6 shrink-0" aria-hidden="true"></span>
            <label class="flex min-w-0 flex-1 items-start gap-3" :class="isDisabled(row.unit) ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'">
              <input
                class="checkbox checkbox-primary checkbox-sm mt-0.5"
                type="checkbox"
                :data-testid="`org-select-${row.unit.id}`"
                :checked="isSelected(row.unit.id)"
                :disabled="isDisabled(row.unit)"
                @change="emit('toggle', row.unit.id, ($event.target as HTMLInputElement).checked)"
              />
              <span class="min-w-0 flex-1">
                <span class="flex flex-wrap items-center gap-2">
                  <span class="font-medium">{{ row.unit.name }}</span>
                  <span class="badge badge-ghost badge-sm">{{ levelLabel(row.unit.level) }}</span>
                  <span v-if="childrenOf(row.unit.id).length" class="text-xs text-base-content/50">{{ descendantCount(units, row.unit.id) }} หน่วยลูก</span>
                </span>
                <span v-if="selectedAncestor(row.unit)" class="mt-1 block text-xs text-info">
                  ครอบคลุมโดย “{{ selectedAncestor(row.unit)?.name }}”
                </span>
                <span v-else-if="blockedByDescendant(row.unit)" class="mt-1 block text-xs text-warning">
                  เลือกไม่ได้ เพราะมีการกำหนดโควต้าที่หน่วยลูกแล้ว
                </span>
              </span>
            </label>
          </div>
          <label v-if="isSelected(row.unit.id)" class="form-control ml-8 mt-3 max-w-xs" :style="{ marginInlineStart: `${row.depth * 1.25 + 2}rem` }">
            <span class="label-text">จำนวนผู้มีสิทธิ์ในโควต้าร่วม</span>
            <input
              class="input input-bordered input-sm"
              type="number"
              min="0"
              required
              :data-testid="`org-quota-${row.unit.id}`"
              :value="quotaCounts[row.unit.id]"
              @input="updateQuota(row.unit.id, $event)"
            />
            <span v-if="descendantCount(units, row.unit.id)" class="mt-1 text-xs text-base-content/60">
              จำนวนนี้ใช้ร่วมกันระหว่างหน่วยนี้และหน่วยลูกทั้งหมด
            </span>
          </label>
        </div>
        <div v-if="!visibleRows.length" class="p-8 text-center text-base-content/60">ไม่พบหน่วยงานที่เลือกได้</div>
      </div>
    </div>

    <aside data-testid="org-quota-summary" class="rounded-box border border-base-300 bg-base-200/40 p-4 xl:sticky xl:top-20 xl:self-start">
      <div class="flex items-center justify-between gap-2">
        <h3 class="font-semibold">สรุปโควต้า</h3>
        <span class="badge badge-primary">{{ selectedUnits.length }} หน่วย</span>
      </div>
      <div v-if="selectedUnits.length" class="mt-3 space-y-3">
        <article v-for="unit in selectedUnits" :key="unit.id" class="rounded-box border border-base-300 bg-base-100 p-3">
          <p class="font-medium">{{ unit.name }}</p>
          <p class="mt-1 text-2xl font-bold text-primary">{{ quotaCounts[unit.id] ?? 0 }} <span class="text-sm font-normal">คน</span></p>
          <p class="text-xs text-base-content/60">
            {{ descendantCount(units, unit.id) ? `โควต้าร่วม ครอบคลุม ${descendantCount(units, unit.id)} หน่วยลูก` : 'โควต้าเฉพาะหน่วยนี้' }}
          </p>
        </article>
      </div>
      <div v-else class="mt-3 rounded-box border border-dashed border-base-300 p-4 text-sm text-base-content/60">
        ยังไม่ได้เลือกหน่วยงาน
      </div>
      <div class="alert alert-info mt-4 py-3 text-xs">
        <span>หน่วยแม่และหน่วยลูกไม่สามารถมีโควต้าแยกกันใน Exam Creation เดียวกัน</span>
      </div>
    </aside>
  </div>
</template>
