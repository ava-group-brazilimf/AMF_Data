---
checklist: bi-developer-checklist
version: 1.0
description: Comprehensive checklist for BI solution development
---

# BI Developer Checklist

## Pre-Development Phase

### Requirements Gathering
- [ ] Business objectives documented
- [ ] User personas identified and documented
- [ ] Key questions/decisions the solution supports are defined
- [ ] Success metrics established
- [ ] Data sources identified and access confirmed
- [ ] Security requirements documented
- [ ] Performance requirements defined

### Data Assessment
- [ ] Source data profiled
- [ ] Data quality issues identified
- [ ] Data refresh frequency requirements confirmed
- [ ] Historical data availability verified
- [ ] Data volume estimated

---

## Semantic Model Development

### Data Model Design
- [ ] Star schema structure implemented
- [ ] Fact tables have clear grain defined
- [ ] Dimension tables are denormalized appropriately
- [ ] Date table created and marked as date table
- [ ] No circular dependencies exist
- [ ] Relationships cardinality correctly set
- [ ] Cross-filter direction appropriate

### Naming Conventions
- [ ] Table names are business-friendly (no abbreviations)
- [ ] Column names are descriptive and consistent
- [ ] Measure names follow naming standard
- [ ] No spaces in column names used for relationships

### Data Types
- [ ] Appropriate data types assigned to all columns
- [ ] Text columns that should be numeric converted
- [ ] Date columns using proper date type
- [ ] Decimal precision appropriate for business needs

### Metadata
- [ ] All tables have descriptions
- [ ] All columns have descriptions
- [ ] Display folders organized logically
- [ ] Hidden columns marked appropriately
- [ ] Sort by column configured where needed

---

## DAX Development

### Measure Quality
- [ ] All measures use DIVIDE() instead of / for division
- [ ] Variables used for readability in complex measures
- [ ] BLANK() handling appropriate
- [ ] No unnecessary CALCULATE wrappers
- [ ] Iterator functions optimized

### Time Intelligence
- [ ] YTD, QTD, MTD measures created
- [ ] Prior period comparisons working
- [ ] YoY, QoQ, MoM growth calculations correct
- [ ] Date table supports all time intelligence

### Documentation
- [ ] Complex measures have comments
- [ ] Measure dependencies documented
- [ ] Business logic explained

---

## Dashboard Development

### Visual Design
- [ ] Clear visual hierarchy established
- [ ] KPIs prominent and contextualized
- [ ] Appropriate chart types selected
- [ ] Consistent color usage
- [ ] White space utilized effectively
- [ ] Grid alignment maintained

### Interactivity
- [ ] Slicers configured appropriately
- [ ] Cross-filtering behavior defined
- [ ] Drill-through pages created where needed
- [ ] Tooltips customized
- [ ] Bookmarks for scenarios created

### User Experience
- [ ] Dashboard answers key business questions
- [ ] Navigation is intuitive
- [ ] Mobile layout created
- [ ] Page load time acceptable (<5 seconds)

### Accessibility
- [ ] Alt text on all visuals
- [ ] Color not only differentiator
- [ ] Sufficient color contrast
- [ ] Tab order logical

---

## Security

### Row-Level Security
- [ ] RLS roles defined
- [ ] RLS tested with different users
- [ ] No data leakage between roles
- [ ] Performance acceptable with RLS

### Workspace Security
- [ ] Workspace roles assigned correctly
- [ ] App permissions configured
- [ ] External sharing settings appropriate

---

## Performance

### Model Optimization
- [ ] Auto date/time disabled
- [ ] Unused columns removed
- [ ] High cardinality columns reviewed
- [ ] Calculated columns minimized
- [ ] Aggregation tables considered

### Query Optimization
- [ ] Visual count per page limited (≤8 recommended)
- [ ] No visual-level filters causing extra queries
- [ ] DirectQuery optimized if used

### Refresh
- [ ] Incremental refresh configured if needed
- [ ] Refresh duration acceptable
- [ ] Refresh schedule appropriate

---

## Testing

### Functional Testing
- [ ] All measures calculate correctly
- [ ] Filters work as expected
- [ ] Drill-through functions properly
- [ ] Bookmarks work correctly
- [ ] Export functionality works

### Data Validation
- [ ] Totals match source system
- [ ] Sampling validation complete
- [ ] Edge cases tested (nulls, zeros)

### User Acceptance
- [ ] UAT with business users complete
- [ ] Feedback incorporated
- [ ] Sign-off obtained

---

## Documentation

### Technical Documentation
- [ ] Data dictionary complete
- [ ] Model diagram created
- [ ] DAX documentation complete
- [ ] Refresh schedule documented

### User Documentation
- [ ] User guide created
- [ ] FAQ documented
- [ ] Training materials prepared

---

## Deployment

### Pre-Deployment
- [ ] Production workspace prepared
- [ ] Naming conventions followed
- [ ] Sensitivity labels applied
- [ ] Gateway configured (if needed)

### Post-Deployment
- [ ] App published
- [ ] Permissions verified
- [ ] Monitoring configured
- [ ] Support process established

---

## Checklist Summary

| Section | Items | Complete |
|---------|-------|----------|
| Pre-Development | 12 | _ / 12 |
| Semantic Model | 18 | _ / 18 |
| DAX | 10 | _ / 10 |
| Dashboard | 14 | _ / 14 |
| Security | 6 | _ / 6 |
| Performance | 9 | _ / 9 |
| Testing | 9 | _ / 9 |
| Documentation | 7 | _ / 7 |
| Deployment | 7 | _ / 7 |
| **TOTAL** | **92** | **_ / 92** |
