<script>
  import { onMount } from 'svelte';
  import { api, VAT_STATUS } from '../lib/api.js';

  let houses = [];
  let catalog = [];
  let rows = [];
  let error = '';
  let fiberFilter = '';
  let form = {
    dyeHouseId: '',
    vatCode: '',
    fiberType: '',
    capacityL: 500,
    status: 'ready',
  };
  let editing = null;

  $: activeFibers = catalog.filter((f) => f.isActive);
  // 编辑中的旧缸可能引用已停用纤维，下拉需能显示原名
  $: editingFiber =
    editing && form.fiberType && !activeFibers.some((f) => f.name === form.fiberType)
      ? form.fiberType
      : '';
  $: selectedFiber = activeFibers.find((f) => f.name === form.fiberType) || null;
  // 过滤下拉取全部名录名（含停用）；名录删除受引用保护，故旧缸纤维名必在名录内
  $: filterOptions = catalog.map((f) => f.name);

  async function load() {
    error = '';
    try {
      const query = fiberFilter ? `?fiberType=${encodeURIComponent(fiberFilter)}` : '';
      [houses, catalog, rows] = await Promise.all([
        api('/dye-houses'),
        api('/fiber-catalog'),
        api(`/vats${query}`),
      ]);
      if (!form.dyeHouseId && houses.length) form.dyeHouseId = String(houses[0].id);
      if (!form.fiberType && activeFibers.length) {
        form.fiberType = activeFibers[0].name;
        form.capacityL = Math.min(form.capacityL, activeFibers[0].capacityLimitL);
      }
    } catch (e) {
      error = e.message;
    }
  }

  onMount(load);

  function houseName(id) {
    return houses.find((h) => h.id === id)?.name || id;
  }

  function onFiberChange() {
    if (selectedFiber && Number(form.capacityL) > selectedFiber.capacityLimitL) {
      form.capacityL = selectedFiber.capacityLimitL;
    }
  }

  async function save() {
    error = '';
    if (!selectedFiber) {
      error = '请选择启用名录中的纤维（停用项不可用于建缸/改缸）';
      return;
    }
    if (Number(form.capacityL) > selectedFiber.capacityLimitL) {
      error = `缸容不得超过该纤维名录上限 ${selectedFiber.capacityLimitL}L`;
      return;
    }
    try {
      const body = {
        dyeHouseId: Number(form.dyeHouseId),
        vatCode: form.vatCode.trim(),
        fiberType: form.fiberType,
        capacityL: Number(form.capacityL),
        status: form.status,
      };
      if (editing) {
        await api(`/vats/${editing}`, { method: 'PUT', body: JSON.stringify(body) });
      } else {
        await api('/vats', { method: 'POST', body: JSON.stringify(body) });
      }
      editing = null;
      form = {
        dyeHouseId: form.dyeHouseId,
        vatCode: '',
        fiberType: activeFibers[0]?.name || '',
        capacityL: 500,
        status: 'ready',
      };
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  function startEdit(row) {
    editing = row.id;
    form = {
      dyeHouseId: String(row.dyeHouseId),
      vatCode: row.vatCode,
      fiberType: row.fiberType,
      capacityL: row.capacityL,
      status: row.status,
    };
  }

  function cancelEdit() {
    editing = null;
    form = {
      dyeHouseId: form.dyeHouseId,
      vatCode: '',
      fiberType: activeFibers[0]?.name || '',
      capacityL: 500,
      status: 'ready',
    };
  }

  async function drain(id) {
    error = '';
    try {
      await api(`/vats/${id}/drain`, { method: 'POST' });
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  async function remove(id) {
    if (!confirm('确认删除该染缸？')) return;
    error = '';
    try {
      await api(`/vats/${id}`, { method: 'DELETE' });
      await load();
    } catch (e) {
      error = e.message;
    }
  }
</script>

<h1 class="page-title">染缸</h1>
<p class="page-sub">
  状态：就绪 / 染色中 / 排液。纤维只能选自<strong>启用名录</strong>，容量（升）不得超过该纤维名录上限。
</p>

<div class="panel" style="margin-bottom:1rem;">
  <div class="form-grid">
    <label
      >所属染坊
      <select bind:value={form.dyeHouseId}>
        {#each houses as h}
          <option value={String(h.id)}>{h.name}</option>
        {/each}
      </select>
    </label>
    <label>缸号 <input bind:value={form.vatCode} /></label>
    <label>
      纤维
      <select bind:value={form.fiberType} on:change={onFiberChange}>
        {#if editingFiber}
          <option value={editingFiber}>{editingFiber}（名录已停用，请改选）</option>
        {/if}
        {#each activeFibers as f}
          <option value={f.name}>{f.name}</option>
        {/each}
      </select>
    </label>
    <label>
      容量 (L){#if selectedFiber}
        <span class="hint">上限 {selectedFiber.capacityLimitL}L</span>
      {/if}
      <input
        type="number"
        step="0.1"
        max={selectedFiber ? selectedFiber.capacityLimitL : undefined}
        bind:value={form.capacityL}
      />
    </label>
    <label
      >状态
      <select bind:value={form.status}>
        <option value="ready">就绪</option>
        <option value="dyeing">染色中</option>
        <option value="drain">排液</option>
      </select>
    </label>
  </div>
  <div class="toolbar">
    <button class="btn" type="button" on:click={save}>{editing ? '保存修改' : '新建染缸'}</button>
    {#if editing}
      <button class="btn ghost" type="button" on:click={cancelEdit}>取消</button>
    {/if}
  </div>
  {#if error}<p class="err">{error}</p>{/if}
</div>

<div class="panel">
  <div class="toolbar">
    <label class="filter">
      按纤维过滤
      <select bind:value={fiberFilter} on:change={load}>
        <option value="">全部</option>
        {#each filterOptions as name}
          <option value={name}>{name}</option>
        {/each}
      </select>
    </label>
  </div>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>染坊</th>
        <th>缸号</th>
        <th>纤维</th>
        <th>容量 L</th>
        <th>状态</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.id}</td>
          <td>{houseName(row.dyeHouseId)}</td>
          <td>{row.vatCode}</td>
          <td>
            {row.fiberType}
            {#if !catalog.find((f) => f.name === row.fiberType && f.isActive)}
              <span class="badge drain" title="名录已停用，旧缸保留原名">停用</span>
            {/if}
          </td>
          <td>{row.capacityL}</td>
          <td><span class="badge {row.status}">{VAT_STATUS[row.status] || row.status}</span></td>
          <td class="row-actions">
            {#if row.status !== 'drain'}
              <button class="btn ghost small" type="button" on:click={() => drain(row.id)}>完成排液</button>
            {/if}
            <button class="btn ghost small" type="button" on:click={() => startEdit(row)}>编辑</button>
            <button class="btn danger small" type="button" on:click={() => remove(row.id)}>删除</button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .filter {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }

  .hint {
    font-size: 0.72rem;
    color: var(--indigo-mist);
  }
</style>
