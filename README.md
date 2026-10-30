# Monitor de Precios: ejecutor independiente

Ejecuta Playwright/Chromium en GitHub Actions para auditar fichas de Sodimac y Prodalam en Temuco, Villarrica, Valdivia, Osorno y Puerto Montt.

En Actions > Auditar precios por sucursal > Run workflow se ejecuta manualmente. También está programado de lunes a viernes a las 12:00 UTC.

Los resultados se descargan en el artefacto `auditoria-sucursales` (CSV, JSON y capturas). **No se extraen precios verificados todavía**: el script busca evidencia de selección de tienda, pero no valida precio ni stock. Nunca usar los resultados como cotizaciones sin confirmación de sucursal y precio.

Este proyecto es independiente de PiscinaSur y no modifica su cotizador ni Vercel.
