# Vy Integration Guide for Governed Mutation Engine

## Overview

This guide explains how Vy (the planner) should interact with the NanoEdit governed mutation engine to safely modify code files.

## Architecture

**Brain (Vy)** → proposes patches  
**NanoEdit** → simulates + compiles + commits  
**Healthcheck** → rolls back if runtime breaks  

## Event Flow

### 1. Code Modification Request

When Vy wants to change code, it should:

1. Parse the repo/file to understand structure
2. Propose **minimal edits** using these parameters:
   - `filePath`: Target file path
   - `operation`: 'replace' (preferred), 'append', or 'overwrite'
   - `searchString`: Existing snippet to anchor (required for replace)
   - `content`: New version
   - `goalId`: ID of the plan/task

3. Send event:
```json
{
  "topic": "code.modify",
  "data": {
    "filePath": "src/example.ts",
    "operation": "replace",
    "searchString": "function oldFunction() {\n  return 'old';\n}",
    "content": "function newFunction() {\n  return 'new';\n}",
    "goalId": "refactor-001"
  }
}
```

### 2. Response Handling

Vy should wait for one of these responses:

#### Success: `code.modified`
```json
{
  "topic": "code.modified",
  "data": {
    "filePath": "/absolute/path/to/file",
    "status": "success",
    "goalId": "refactor-001",
    "backupLocation": "/absolute/path/to/file.bak"
  }
}
```
→ **Action**: Continue with next step

#### Failure: `code.failure`
```json
{
  "topic": "code.failure",
  "data": {
    "filePath": "/absolute/path/to/file",
    "error": "Structural Lock: searchString not found in file",
    "goalId": "refactor-001"
  }
}
```
→ **Action**: Rethink the edit, simplify, or break into smaller patches

#### Rollback: `code.rollback`
```json
{
  "topic": "code.rollback",
  "data": {
    "filePath": "/absolute/path/to/file",
    "reason": "Healthcheck failed after code modification",
    "goalId": "refactor-001",
    "rollbackSuccess": true
  }
}
```
→ **Action**: Rethink the edit approach, the change broke runtime behavior

## Safety Mechanisms

### 1. Structural Lock
- **Replace operations** require exact `searchString` match
- If not found → immediate failure
- **Best Practice**: Use distinctive, stable code snippets as anchors

### 2. TypeScript Compiler Gate
- All `.ts`/`.tsx` files are compiled after editing
- Compilation errors → automatic rollback
- **Best Practice**: Ensure type safety in proposed changes

### 3. VDR Complexity Gate
- Growth factor limit: `newContent.length / searchString.length ≤ 8`
- Prevents explosive complexity increases
- **Best Practice**: Keep replacements proportional to original size

### 4. Runtime Healthcheck
- Automatic testing after successful edits
- Tries `npm test` then `curl localhost:3000/health`
- Failure → automatic rollback to `.bak` file

## Best Practices for Vy

### 1. Prefer Replace Operations
```json
{
  "operation": "replace",
  "searchString": "// Exact code to find",
  "content": "// New code to replace with"
}
```

### 2. Use Distinctive Anchors
- Choose unique function signatures, class names, or comments
- Avoid generic patterns like `const x =`

### 3. Atomic Changes
- One logical change per edit
- Break large refactors into smaller steps

### 4. Error Recovery
- On `Structural Lock`: Re-examine file, update searchString
- On `Entropy Violation`: Split into smaller changes
- On `TypeScript Error`: Fix type issues in content
- On `Healthcheck Failure`: Review runtime impact

## Audit Trail

All successful edits are logged to `nanoedit.log.jsonl`:
```json
{"filePath":"/path/to/file","goalId":"refactor-001","timestamp":"2025-12-02T...","operation":"replace"}
```

TS/JS files also get watermark comments:
```javascript
// [NanoEdit] goalId=refactor-001 at 2025-12-02T10:30:00.000Z
```

## Example Workflow

1. **Vy analyzes** `src/utils.ts`
2. **Vy proposes** replace operation for specific function
3. **NanoEdit** creates `.shadow` file with changes
4. **NanoEdit** runs TypeScript compiler check
5. **NanoEdit** commits `.shadow` → main file, creates `.bak`
6. **Healthcheck** runs tests/health endpoint
7. **Success**: Change is live, audit logged
8. **Failure**: Automatic rollback from `.bak`

This ensures safe, traceable, and reversible code mutations.