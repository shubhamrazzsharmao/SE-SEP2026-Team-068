import Link from "next/link";
import { LuPlus } from "react-icons/lu";
import { EmptyState } from "@/app/empty-state";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { Card, LinkButton, PageHeader, Pill } from "@/components/ui/layout";
import { updateBrand } from "@/lib/actions";
import { getBrand, getMe, listCampaigns } from "@/lib/api/queries";
import { ROLE_LABEL } from "@/lib/format";
import { BrandFields } from "../brand-fields";

export default async function ClientPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [me, brand, campaigns] = await Promise.all([getMe(), getBrand(id), listCampaigns()]);
  const mine = brand.owner_id === me.id;
  const brandCampaigns = campaigns.filter((c) => c.brand_id === brand.id);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <PageHeader
        back={{ href: "/clients", label: "Clients" }}
        title={brand.name}
        actions={mine && <LinkButton href={`/campaigns/new?brand=${brand.id}`}><LuPlus size={16} /> New campaign</LinkButton>}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Campaigns" className="lg:col-span-2">
          {brandCampaigns.length === 0 ? (
            <EmptyState title="No campaigns yet" text={mine ? "Start one with the New campaign button." : "You aren't a member of any campaign for this client."} />
          ) : (
            <ul className="divide-y divide-line">
              {brandCampaigns.map((c) => (
                <li key={c.id}>
                  <Link href={`/campaigns/${c.id}`} className="flex items-center justify-between gap-3 py-3 hover:text-brand">
                    <span className="font-medium">{c.name}</span>
                    <Pill>{ROLE_LABEL[c.my_role]}</Pill>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Brand guidelines">
          <ActionForm action={updateBrand.bind(null, brand.id)}>
            <BrandFields brand={brand} />
            <SubmitButton className="mt-5 w-full" pendingText="Saving…">Save guidelines</SubmitButton>
          </ActionForm>
          <p className="mt-3 text-xs text-muted">
            Only the brand owner or a campaign brand manager can save. Changes apply to content generated afterwards.
          </p>
        </Card>
      </div>
    </div>
  );
}
