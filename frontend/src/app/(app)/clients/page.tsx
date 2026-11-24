import Link from "next/link";
import { EmptyState } from "@/app/empty-state";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { Card, PageHeader } from "@/components/ui/layout";
import { createBrand } from "@/lib/actions";
import { getMe, listBrands, listCampaigns } from "@/lib/api/queries";
import { BrandFields } from "./brand-fields";

export default async function ClientsPage() {
  const me = await getMe();
  const [brands, campaigns] = await Promise.all([listBrands(), listCampaigns()]);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <PageHeader title="Clients" description="Each client is a brand with its own voice and word lists." />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-3 lg:col-span-2">
          {brands.length === 0 ? (
            <EmptyState title="No clients yet" text="Add your first client brand to start a campaign." />
          ) : (
            brands.map((b) => {
              const count = campaigns.filter((c) => c.brand_id === b.id).length;
              return (
                <Link key={b.id} href={`/clients/${b.id}`}
                  className="block rounded-3xl border border-line bg-white p-5 transition-transform duration-200 hover:-translate-y-0.5">
                  <div className="flex items-start justify-between gap-3">
                    <h2 className="text-lg font-semibold">{b.name}</h2>
                    <span className="text-xs font-medium text-muted">
                      {b.owner_id === me.id ? "Owner" : "Shared with you"} · {count} campaign{count === 1 ? "" : "s"}
                    </span>
                  </div>
                  <p className="mt-1 line-clamp-2 text-sm text-muted">{b.tone}</p>
                </Link>
              );
            })
          )}
        </div>

        <Card title="New client">
          <ActionForm action={createBrand}>
            <BrandFields />
            <SubmitButton className="mt-5 w-full" pendingText="Saving…">Add client</SubmitButton>
          </ActionForm>
        </Card>
      </div>
    </div>
  );
}
