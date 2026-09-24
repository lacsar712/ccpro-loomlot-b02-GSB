<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import { user } from '../lib/auth.js';

  let rows = [];
  let error = '';
  let form = { name: '', isActive: true, capacityLimitL: 500 };
  let editing = null;

  $: isAdmin = $user?.role === 'admin';

  async function load() {
    error = '';
    try {
      rows = await api('/fiber-catalog');
    } catch (e) {
      error = e.message;
    }
  }

  onMount(load);

  function resetForm() {
    editing = null;
    form = { name: '', isActive: true, capacityLimitL: 500 };
  }

  async function save() {
    error = '';
    const body = {
      name: form.name.trim(),
      isActive: !!form.isActive,
      capacityLimitL: Number(form.capacityLimitL),
    };
    if (!body.name) {
      error = '纤维名不能为空';
      return;
    }
    if (!(body.capacityLimitL > 0)) {
      error = '缸容上限必须为正数';
      return;
    }
    try {
      if (editing) {
        await api(`/fiber-catalog/${editing}`, { method: 'PUT', body: JSON.stringify(body) });
      } else {
        await api('/fiber-catalog', { method: 'POST', body: JSON.stringify(body) });
      }
      resetForm();
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  function startEdit(row) {
    editing = row.id;
    form = {
      name: row.name,
      isActive: row.isActive,
      capacityLimitL: row.capacityLimitL,
    };
  }

  async function toggleActive(row) {
    error = '';
    try {
      await api(`/fiber-catalog/${row.id}`, {
        method: 'PUT',
        body: JSON.stringify({ isActive: !row.isActive }),
      });
      await load();
    } catch (e) {
      error = e.message;
    }
  }

  async function remove(row) {
    if (!confirm(`确认删除纤维「${row.name}」？停用可保留旧缸记录，删除则不可恢复。`)) return;
    error = '';
    try {
      await api(`/fiber-catalog/${row.id}`, { method: 'DELETE' });
      await load();
    } catch (e) {
      error = e.message;
    }
  }
</script>

<h1 class="page-title">纤维名录</h1>
<p class="page-sub">
  全场维护的纤维白名单。缸容上限（升）= 该纤维允许的<strong>单缸最大容量</strong>，建缸/改缸容量不得超过此值；停用后不可再选入新缸或改缸，旧缸仍显示原名。
</p>

{#if isAdmin}
  <div class="panel" style="margin-bottom:1rem;">
    <div class="form-grid">
      <label>纤维名 <input bind:value={form.name} placeholder="去空白后唯一" /></label>
      <label
        >缸容上限 (L)
        <input type="number" min="0" step="0.1" bind:value={form.capacityLimitL} />
      </label>
      <label class="check">
        启用
        <input type="checkbox" bind:checked={form.isActive} />
      </label>
    </div>
    <div class="toolbar">
      <button class="btn" type="button" on:click={save}>{editing ? '保存修改' : '新增名录项'}</button>
      {#if editing}
        <button class="btn ghost" type="button" on:click={resetForm}>取消</button>
      {/if}
    </div>
    {#if error}<p class="err">{error}</p>{/if}
  </div>
{:else}
  <div class="panel" style="margin-bottom:1rem;">
    <p style="margin:0;color:var(--indigo-mist);font-size:0.88rem;">
      当前为操作员视图，仅染坊主管可维护名录；建缸时纤维只能选自下方启用项。
    </p>
    {#if error}<p class="err">{error}</p>{/if}
  </div>
{/if}

<div class="panel">
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
          <td>{row.name}</td>
          <td>
            {#if row.isActive}
              <span class="badge ready">启用</span>
            {:else}
              <span class="badge drain">停用</span>
            {/if}
          </td>
          <td>{row.capacityLimitL}</td>
          {#if isAdmin}
            <td class="row-actions">
              <button class="btn ghost small" type="button" on:click={() => toggleActive(row)}>
                {row.isActive ? '停用' : '启用'}
              </button>
              <button class="btn ghost small" type="button" on:click={() => startEdit(row)}>编辑</button>
              <button class="btn danger small" type="button" on:click={() => remove(row)}>删除</button>
            </td>
          {/if}
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .check {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }

  .check input {
    width: 1.1rem;
    height: 1.1rem;
  }
</style>
