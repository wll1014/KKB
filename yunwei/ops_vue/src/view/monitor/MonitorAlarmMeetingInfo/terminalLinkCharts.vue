<template>
	<div style="width: 230px;height: 30px;">
		<svg class='linkTest' style="width: 230px;height: 42px;">
			<defs>
				<marker viewBox="0 0 5 5" markerWidth="5" markerHeight="5" orient="auto" refX="5" refY="2.5" id="markerArrowBlock">
					<!-- 闭合箭头实心三角形 -->
					<path d="M 0 0 L 5 2.5 L 0 5 z"></path>
				</marker>
			</defs>
		<line
			:x1="0"
			:x2="230"
			:y1="21"
			:y2="21"
			stroke="#5eb9ef"
			fill="none" 
			style="stroke-width: 1px; marker-end: url(#markerArrowBlock);"></line>
			</svg>
	</div>
</template>

<script>
</script>

<style>
	.linkTest marker path {
		fill:#5eb9ef
	}
</style>
