// Error page rendering for SSR failures

export function renderErrorPage(): string {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Error — Fund Analytics Dashboard</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: #f5f5f5;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 1rem;
    }
    .error-container {
      background: white;
      border-radius: 0.5rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      padding: 2rem;
      max-width: 28rem;
      text-align: center;
    }
    h1 {
      font-size: 2.25rem;
      font-weight: bold;
      margin-bottom: 0.5rem;
    }
    h2 {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }
    p {
      font-size: 0.875rem;
      color: #6b7280;
      margin-bottom: 1.5rem;
    }
    a {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 0.375rem;
      background: #3b82f6;
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
      font-weight: 500;
      color: white;
      text-decoration: none;
      transition: background-color 0.2s;
    }
    a:hover {
      background: #2563eb;
    }
  </style>
</head>
<body>
  <div class="error-container">
    <h1>500</h1>
    <h2>Server Error</h2>
    <p>An unexpected error occurred while loading the dashboard.</p>
    <a href="/">Go home</a>
  </div>
</body>
</html>
  `.trim();
}
