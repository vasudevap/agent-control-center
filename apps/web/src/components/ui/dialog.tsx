"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export function DialogContent({ className, children, ...props }: React.ComponentProps<typeof DialogPrimitive.Content>) {
  return <DialogPrimitive.Portal><DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-foreground/30" /><DialogPrimitive.Content className={cn("fixed left-1/2 top-1/2 z-50 grid max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 gap-5 overflow-y-auto overscroll-contain rounded-atlas-lg border border-border-strong bg-surface p-5 shadow-atlas-md sm:p-6", className)} {...props}>{children}<DialogPrimitive.Close className="absolute right-4 top-4 rounded-atlas-sm p-1 text-foreground-tertiary hover:bg-surface-hover hover:text-foreground" aria-label="Close dialog"><X className="size-4" aria-hidden="true" /></DialogPrimitive.Close></DialogPrimitive.Content></DialogPrimitive.Portal>;
}
export function DialogHeader(props: React.ComponentProps<"div">) { return <div {...props} className={cn("flex flex-col gap-2 pr-8", props.className)} />; }
export function DialogFooter(props: React.ComponentProps<"div">) { return <div {...props} className={cn("flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", props.className)} />; }
export function DialogTitle(props: React.ComponentProps<typeof DialogPrimitive.Title>) { return <DialogPrimitive.Title {...props} className={cn("text-lg font-semibold text-foreground", props.className)} />; }
export function DialogDescription(props: React.ComponentProps<typeof DialogPrimitive.Description>) { return <DialogPrimitive.Description {...props} className={cn("text-sm leading-relaxed text-foreground-secondary", props.className)} />; }
