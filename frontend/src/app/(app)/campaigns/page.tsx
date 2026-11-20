import { LuPlus } from "react-icons/lu";
import { CampaignList } from "@/components/dashboard/campaign-list";
import { LinkButton, PageHeader } from "@/components/ui/layout";
import { getDashboard } from "@/lib/api/dashboard";

export default async function CampaignsPage() {
  const { campaigns } = await getDashboard();
  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <PageHeader
        title="Campaigns"
        description="Every campaign you belong to, with your role in it."
        actions={<LinkButton href="/campaigns/new"><LuPlus size={16} /> New campaign</LinkButton>}
      />
      <CampaignList campaigns={campaigns} heading={null} />
    </div>
  );
}
