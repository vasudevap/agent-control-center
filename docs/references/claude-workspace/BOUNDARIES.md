# BOUNDARIES.md

# Purpose

Defines the responsibilities of Claude while working on Atlas.

---

# Claude Owns

- Product UI
- UX
- Layout
- Components
- Design System
- Typography
- Color
- Motion
- Accessibility
- Responsive behavior
- React implementation
- Tailwind implementation
- shadcn/ui composition

---

# Claude Does NOT Own

Do not invent or redefine:

- APIs
- Backend architecture
- Database schema
- Authentication
- Authorization
- Infrastructure
- Deployment
- WebSocket strategy
- Caching strategy
- Monitoring
- Performance budgets
- Security architecture

These belong to the Architecture repository.

If implementation depends on one of these, use realistic mock data and clearly identify the assumption.

---

# Rule

When uncertain:

Implement the UI.

Do not redesign the product.
