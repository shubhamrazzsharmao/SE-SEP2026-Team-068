import { FaFacebookF, FaInstagram, FaLinkedinIn } from "react-icons/fa6";
import { LuPenLine } from "react-icons/lu";
import type { Platform } from "@/types/app";

const map: Record<Platform, { Icon: typeof LuPenLine; cls: string }> = {
  linkedin: { Icon: FaLinkedinIn, cls: "bg-accent text-white" },
  instagram: { Icon: FaInstagram, cls: "bg-brand text-white" },
  facebook: { Icon: FaFacebookF, cls: "bg-blue-600 text-white" },
  blog: { Icon: LuPenLine, cls: "bg-ink text-paper" },
};

export function PlatformIcon({ platform }: { platform: Platform }) {
  const { Icon, cls } = map[platform];
  return (
    <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg ${cls}`}>
      <Icon size={15} />
    </span>
  );
}
