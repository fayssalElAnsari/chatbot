import { z } from "zod"

export const documentSchema = z.object({
  id: z.string(),
  text: z.string(),
  status: z.string(),
  label: z.string(),
  filename: z.string()
})

export type Document = z.infer<typeof documentSchema>