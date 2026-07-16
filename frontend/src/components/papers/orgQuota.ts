export interface QuotaOrgUnit {
  id: string;
  code: string;
  name: string;
  level: string;
  parent_id: string | null;
  status: string;
}

export function findSelectedAncestor(
  units: QuotaOrgUnit[],
  selectedIds: string[],
  orgUnitId: string,
): QuotaOrgUnit | null {
  const byId = new Map(units.map((unit) => [unit.id, unit]));
  const selected = new Set(selectedIds);
  const visited = new Set<string>();
  let parentId = byId.get(orgUnitId)?.parent_id ?? null;

  while (parentId && !visited.has(parentId)) {
    visited.add(parentId);
    const parent = byId.get(parentId);
    if (!parent) return null;
    if (selected.has(parent.id)) return parent;
    parentId = parent.parent_id;
  }
  return null;
}

export function hasSelectedDescendant(
  units: QuotaOrgUnit[],
  selectedIds: string[],
  orgUnitId: string,
): boolean {
  const selected = new Set(selectedIds);
  const children = new Map<string, string[]>();
  for (const unit of units) {
    if (!unit.parent_id) continue;
    children.set(unit.parent_id, [...(children.get(unit.parent_id) ?? []), unit.id]);
  }
  const queue = [...(children.get(orgUnitId) ?? [])];
  const visited = new Set<string>();
  while (queue.length) {
    const id = queue.shift()!;
    if (visited.has(id)) continue;
    visited.add(id);
    if (selected.has(id)) return true;
    queue.push(...(children.get(id) ?? []));
  }
  return false;
}

export function hasQuotaOverlap(units: QuotaOrgUnit[], selectedIds: string[]): boolean {
  return selectedIds.some((id) => findSelectedAncestor(units, selectedIds, id) !== null);
}

export function descendantCount(units: QuotaOrgUnit[], orgUnitId: string): number {
  const children = new Map<string, string[]>();
  for (const unit of units) {
    if (!unit.parent_id) continue;
    children.set(unit.parent_id, [...(children.get(unit.parent_id) ?? []), unit.id]);
  }
  const queue = [...(children.get(orgUnitId) ?? [])];
  const visited = new Set<string>();
  while (queue.length) {
    const id = queue.shift()!;
    if (visited.has(id)) continue;
    visited.add(id);
    queue.push(...(children.get(id) ?? []));
  }
  return visited.size;
}
