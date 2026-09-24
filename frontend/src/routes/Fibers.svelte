<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import { user } from '../lib/auth.js';

  $: isAdmin = $user?.role === 'admin';

  let rows = [];
  let error = '';
  let form = { fiberName: '', enabled: true, maxCapacityL: 500 };
  let editing = null;

  $: enabledCount = rows.filter((r) => r.enabled).length;

  async function load() {
    error = '';
    try {
      rows = await api('/fiber-catalog');
    } catch (e) {
      error = e.message;
    }
  }

  onMount(load);

  async function save() {
    error = '';
    try {
      const body = {
        fiberName: form.fiberName.trim(),
        enabled: !!form.enabled,
        maxCapacityL: Number(form.maxCapacityL),
      };
      if (editing) {
        await api(`/fiber-catalog/${editing}`, { method: 'PUT', body: JSON.stringify(body) });
      } else {
        await api('/fiber-catalog', { method: 'POST', body: JSON.stringify(body) });
      }
      form = { fiberName: '', enabled: true, maxCapacityL: 500 };
      editing = null;
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  function startEdit(row) {
    editing = row.id;
    form = {
      fiberName: row.fiberName,
      enabled: row.enabled,
      maxCapacityL: row.maxCapacityL,
    };
  }

  async function toggleEnabled(row) {
    error = '';
    try {
      await api(`/fiber-catalog/${row.id}`, {
        method: 'PUT',
        body: JSON.stringify({ enabled: !row.enabled }),
      });
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  async function remove(id) {
    if (!confirm('确认删除该名录项？已建染缸仍保留原纤维名。')) return;
    error = '';
    try {
      await api(`/fiber-catalog/${id}`, { method: 'DELETE' });
      await load();
    } catch (e) {
      error = e.message;
    }
  }
</script>

<h1 class="page-title">纤维名录</h1>
<p class="page-sub">
  缸容上限：该纤维允许的最大缸容升数，建缸或改缸时容量不得超过。停用后不可再选入新缸或改缸，旧缸仍显示原名。
</p>

{#if isAdmin}
  <div class="panel" style="margin-bottom:1rem;">
    <div class="form-grid">
      <label>纤维名 <input bind:value={form.fiberName} placeholder="如：棉" /></label>
      <label
        >缸容上限 (L) <input type="number" step="0.1" min="0" bind:value={form.maxCapacityL} /></label
      >
      <label
        >启用
        <select bind:value={form.enabled}>
          <option value={true}>启用</option>
          <option value={false}>停用</option>
        </select>
      </label>
    </div>
    <div class="toolbar">
      <button class="btn" type="button" on:click={save}>{editing ? '保存修改' : '新登名录'}</button>
      {#if editing}
        <button
          class="btn ghost"
          type="button"
          on:click={() => {
            editing = null;
            form = { fiberName: '', enabled: true, maxCapacityL: 500 };
          }}>取消</button
        >
      {/if}
    </div>
    {#if error}<p class="err">{error}</p>{/if}
  </div>
{:else}
  <p class="page-sub" style="margin-bottom:1rem;">名录由染坊主管维护；建缸时仅可选用启用项。</p>
  {#if error}<p class="err">{error}</p>{/if}
{/if}

<div class="panel">
  <p style="margin:0 0 0.75rem;color:var(--indigo-mist);font-size:0.85rem;">
    启用 <strong>{enabledCount}</strong> / 共 {rows.length} 条（与总览「启用纤维」一致）
  </p>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>纤维名</th>
        <th>状态</th>
        <th>缸容上限 L</th>
        {#if isAdmin}<th></th>{/if}
      </tr>
    </thead>
    <tbody>
      {#each rows as row}
        <tr>
          <td>{row.id}</td>
          <td>{row.fiberName}</td>
          <td>
            <span class="badge" class:ready={row.enabled} class:drain={!row.enabled}>
              {row.enabled ? '启用' : '停用'}
            </span>
          </td>
          <td>{row.maxCapacityL}</td>
          {#if isAdmin}
            <td class="row-actions">
              <button class="btn ghost small" type="button" on:click={() => toggleEnabled(row)}>
                {row.enabled ? '停用' : '启用'}
              </button>
              <button class="btn ghost small" type="button" on:click={() => startEdit(row)}>编辑</button>
              <button class="btn danger small" type="button" on:click={() => remove(row.id)}>删除</button>
            </td>
          {/if}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
