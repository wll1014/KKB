<template>
  <div class="components-table-nest">
    <table>
      <!-- 关键代码 start -->
      <colgroup>
        <col v-for="(conf,index) in tableConf" :width="conf.width">
      </colgroup>
      <!-- 关键代码 end -->
      <thead>
      <tr>
        <th v-for="(conf,index) in tableConf">
          <SpanOverflowEllipsis :content="conf.title"></SpanOverflowEllipsis>
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(row,index) in data">
        <td v-for="conf in tableConf">
          <SpanOverflowEllipsis :content="row[conf.prop]"></SpanOverflowEllipsis>
        </td>
      </tr>
      </tbody>
    </table>
    <div class="no-data"
         v-if="!data || data.length ===0">{{emptyText}}</div>
  </div>
</template>

<script>
  export default {
    name: "TableNest",
    components: {
      SpanOverflowEllipsis: () => import('@/components/common/SpanOverflowEllipsis.vue'),
    },
    props: {
      tableConf: {
        type: Array,
        default: [],
      },
      data: {
        type: Array,
        default: [],
      },
      emptyText: {
        type: String,
        default: '暂无数据'
      },
    },
  }
</script>

<style>
  .components-table-nest {
    overflow: auto;
  }

  .components-table-nest table {
    width: 100%;
    border-collapse: collapse;
    border-spacing: 0;
    /* 必须要设置为fixed，这样列宽就可以由表格宽度和列宽度设定了 */
    table-layout: fixed;
  }

  .components-table-nest table th {
    text-align: left;
    padding: 2px 4px;
  }

  .components-table-nest table td {
    text-align: left;
    padding: 2px 4px;
  }

  .components-table-nest tbody tr:nth-of-type(odd) {
    background-color: #292e30;
  }

  .components-table-nest tbody tr:nth-of-type(even) {
    background-color: #232629;
  }

  .components-table-nest .no-data {
    width: 100%;
    text-align: center;
    padding: 10px 0px;
  }
</style>
