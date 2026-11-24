import { Input, Textarea } from "@/components/ui/fields";
import type { BrandOut } from "@/types/api";

export function BrandFields({ brand }: { brand?: BrandOut }) {
  return (
    <div className="space-y-4">
      <Input label="Client / brand name" name="name" required maxLength={150} defaultValue={brand?.name} placeholder="Nova Fitness" />
      <Textarea label="Tone of voice" name="tone" required maxLength={5000} defaultValue={brand?.tone}
        placeholder="Warm, practical, no jargon" hint="Used for every piece generated for this client." />
      <Textarea label="Preferred terms" name="preferred_terms" rows={2} defaultValue={brand?.preferred_terms.join(", ")}
        placeholder="members, coaching, community" hint="Comma-separated. The AI will use these." />
      <Textarea label="Terms to avoid" name="avoided_terms" rows={2} defaultValue={brand?.avoided_terms.join(", ")}
        placeholder="cheap, guaranteed results" hint="Comma-separated. The AI will never use these." />
    </div>
  );
}
