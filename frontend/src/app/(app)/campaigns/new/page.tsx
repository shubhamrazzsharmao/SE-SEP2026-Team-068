import Link from "next/link";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { Input, Select, Textarea } from "@/components/ui/fields";
import { Card, PageHeader } from "@/components/ui/layout";
import { createCampaign } from "@/lib/actions";
import { getMe, listBrands } from "@/lib/api/queries";

export default async function NewCampaignPage({ searchParams }: { searchParams: Promise<{ brand?: string }> }) {
  const [{ brand }, me, brands] = await Promise.all([searchParams, getMe(), listBrands()]);
  // The backend only lets you create campaigns under brands you own.
  const owned = brands.filter((b) => b.owner_id === me.id);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader back={{ href: "/campaigns", label: "Campaigns" }} title="New campaign"
        description="You'll be the owner. Add creators and reviewers afterwards." />
      <Card>
        {owned.length === 0 ? (
          <p className="text-sm text-muted">
            You need a client brand first.{" "}
            <Link href="/clients" className="font-semibold text-brand hover:underline">Add a client</Link>
          </p>
        ) : (
          <ActionForm action={createCampaign} className="space-y-4">
            <Select label="Client" name="brand_id" required defaultValue={brand ?? String(owned[0].id)}>
              {owned.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </Select>
            <Input label="Campaign name" name="name" required maxLength={150} placeholder="Winter Challenge launch" />
            <Textarea label="Description" name="description" maxLength={2000} placeholder="Optional: goal, dates, anything the team should know." />
            <SubmitButton pendingText="Creating…">Create campaign</SubmitButton>
          </ActionForm>
        )}
      </Card>
    </div>
  );
}
