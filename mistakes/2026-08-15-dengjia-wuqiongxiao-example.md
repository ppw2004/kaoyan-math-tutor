---
date: 2026-08-15
chapter: 极限
topic: 等价无穷小替换
difficulty: ★★☆
wrong_count: 1
interval_days: 1
next_review: 2026-08-16
tags: [泰勒展开, 加减抵消]
status: active
---

# tanx−sinx 三阶无穷小（示例错题，可删除）

## 原题

求 $\lim_{x\to 0}\dfrac{\tan x-\sin x}{x^3}$。

## 我的错误做法 / 卡点

把 $\tan x\sim x$、$\sin x\sim x$ 直接代入分子，得 $\frac{x-x}{x^3}=0$。

## 错因

概念不清：等价无穷小替换只保证乘除安全，加减时主部可能抵消，差的高阶信息丢失。

## 正确思路关键步

分子有理化或泰勒展开：$\tan x-\sin x = \tan x(1-\cos x) \sim x\cdot\frac{x^2}{2}$。

## 重做记录

| 日期 | 结果 | 备注 |
|------|------|------|
