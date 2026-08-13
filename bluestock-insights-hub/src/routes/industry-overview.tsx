import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/industry-overview")({
  beforeLoad: () => {
    throw redirect({ to: "/" });
  },
});
