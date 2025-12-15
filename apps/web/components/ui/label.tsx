import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const labelVariants = cva(
    "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
)

const Label = React.forwardRef<
    React.ElementRef<typeof LabelPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root> &
    VariantProps<typeof labelVariants>
// Assuming LabelPrimitive is imported or we use simple label
>(({ className, ...props }, ref) => (
    <label
        ref={ref}
        className={cn(labelVariants(), className)}
        {...props}
    />
))
// Wait, I need @radix-ui/react-label
// The package.json says "^2.0.2" so it's there.
// I should import it.
import * as LabelPrimitive from "@radix-ui/react-label"

const LabelReal = React.forwardRef<
    React.ElementRef<typeof LabelPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root> &
    VariantProps<typeof labelVariants>
>(({ className, ...props }, ref) => (
    <LabelPrimitive.Root
        ref={ref}
        className={cn(labelVariants(), className)}
        {...props}
    />
))
LabelReal.displayName = LabelPrimitive.Root.displayName

export { LabelReal as Label }
