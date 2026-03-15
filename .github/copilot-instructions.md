---
description: AI rules derived by SpecStory from the project AI interaction history
applyTo: *
---

## PROJECT OVERVIEW

This document defines the rules, coding standards, workflow guidelines, references, documentation structures, and best practices for the project. It serves as a living document, evolving with the project and incorporating new guidelines and decisions as they arise.

## CODE STYLE

(Currently no specific code style rules defined.)

## FOLDER ORGANIZATION

(Currently no specific folder organization rules defined.)

## TECH STACK

(Currently no specific tech stack defined.)

## PROJECT-SPECIFIC STANDARDS

When running 10 parallel agents, `CLAUDE.md` becomes the single source of truth that keeps all agents aligned. Without it, agents make contradictory decisions.

When `CLAUDE.md` files are too long and Claude ignores instructions, split into `CLAUDE.md` (universal rules) + skill files (domain-specific). Use `@imports` for structure. Keep root `CLAUDE.md` under 50 lines. If `CLAUDE.md` bloat persists, implement a pre-commit hook that rejects `CLAUDE.md` files over the line limit.

## WORKFLOW & RELEASE RULES

When running parallel agents well requires a different mental model than running one. You're not a developer using a tool anymore. You're an orchestrator managing a team. Some people will get that immediately. Some will need more time. The plan has to account for both.

## REFERENCE EXAMPLES

(Currently no reference examples defined.)

## PROJECT DOCUMENTATION & CONTEXT SYSTEM

When using multiple agents, a shared standard for context files (`CLAUDE.md`) is essential. The team should build the template together to ensure buy-in. One agent with bad context is annoying; ten agents with bad context is a disaster.

When `CLAUDE.md` files are too long and Claude ignores instructions, split into `CLAUDE.md` (universal rules) + skill files (domain-specific). Use `@imports` for structure. Keep root `CLAUDE.md` under 50 lines. If `CLAUDE.md` bloat persists, implement a pre-commit hook that rejects `CLAUDE.md` files over the line limit.

## DEBUGGING

When running multiple parallel agents, document every failure in a shared log so the team is learning collectively, not just individually. Identify failure modes like merge conflicts, contradictory implementations, and context drift.

## FINAL DOs AND DON'Ts

(Currently no specific DOs and DON'Ts defined.)