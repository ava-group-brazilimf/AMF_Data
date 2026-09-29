---
task: create-row-level-security
version: 1.0
elicit: true
description: Design and implement Row-Level Security (RLS) for Power BI datasets
---

# Create Row-Level Security

## Purpose
Design and implement Row-Level Security (RLS) to ensure users only see data they are authorized to access.

## Process

### Step 1: Gather Requirements
ASK the user for:

1. **Security Model**: What determines data access? (Region, Department, Manager hierarchy)
2. **User Groups**: What groups/roles exist?
3. **Access Rules**: What data should each group see?
4. **Dynamic vs Static**: Should rules be user-specific or group-based?
5. **Hierarchy**: Is there manager/employee hierarchy to consider?

### Step 2: Design Security Model

**Static RLS (Group-based)**
```dax
// Role: West Region
[Region] = "West"

// Role: Sales Department
[Department] = "Sales"
```

**Dynamic RLS (User-based)**
```dax
// Filter based on logged-in user's email
[SalesPersonEmail] = USERPRINCIPALNAME()

// Or using a security table
CONTAINS(
    SecurityTable,
    SecurityTable[UserEmail], USERPRINCIPALNAME(),
    SecurityTable[Region], [Region]
)
```

### Step 3: Generate Implementation

PRODUCE the following:

1. **Security Roles Definition**
```yaml
roles:
  - name: "Regional Manager - West"
    description: "Access to West region data only"
    tables:
      - name: Sales
        filter_expression: "[Region] = \"West\""
      - name: Customers
        filter_expression: "[Region] = \"West\""
    
  - name: "Dynamic User Security"
    description: "Users see only their assigned data"
    tables:
      - name: Sales
        filter_expression: |
          VAR CurrentUser = USERPRINCIPALNAME()
          RETURN
          [AssignedTo] = CurrentUser ||
          CONTAINS(
              UserSecurity,
              UserSecurity[Email], CurrentUser,
              UserSecurity[Region], [Region]
          )
```

2. **Security Table Design**
```sql
CREATE TABLE UserSecurity (
    UserEmail VARCHAR(255),
    Region VARCHAR(50),
    Department VARCHAR(50),
    AccessLevel VARCHAR(20),
    EffectiveDate DATE,
    ExpirationDate DATE
);
```

3. **Testing Scenarios**
```yaml
test_cases:
  - user: "john@company.com"
    role: "West Region"
    expected_regions: ["West"]
    expected_rows: "~10,000"
    
  - user: "manager@company.com"
    role: "All Regions"
    expected_regions: ["West", "East", "Central"]
    expected_rows: "~50,000"
```

## RLS Patterns

### Pattern 1: Simple Field Filter
```dax
[Department] = "Finance"
```

### Pattern 2: Dynamic User Lookup
```dax
[OwnerEmail] = USERPRINCIPALNAME()
```

### Pattern 3: Security Table Lookup
```dax
CONTAINS(
    UserSecurity,
    UserSecurity[UserEmail], USERPRINCIPALNAME(),
    UserSecurity[Region], [Region]
)
```

### Pattern 4: Manager Hierarchy (Parent-Child)
```dax
VAR CurrentUser = USERPRINCIPALNAME()
VAR UserPath = 
    LOOKUPVALUE(
        Employees[Path],
        Employees[Email], CurrentUser
    )
RETURN
PATHCONTAINS(UserPath, [EmployeeID])
```

## Output Structure

```
rls/
├── design/
│   ├── security-model.md
│   ├── role-definitions.yaml
│   └── security-table-design.sql
├── implementation/
│   ├── dax-expressions.dax
│   └── test-cases.md
├── docs/
│   └── rls-admin-guide.md
└── README.md
```

## Quality Criteria

- [ ] All user groups have defined roles
- [ ] No data leakage between roles
- [ ] Performance acceptable with RLS applied
- [ ] Testing completed for all scenarios
- [ ] Documentation complete for admins
