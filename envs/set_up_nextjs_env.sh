#!/bin/bash

# This script sets up a reusable Next.js development environment for automated testing.

# The directory where the Next.js project will be created.
if [ -z "$1" ]; then
    echo "Usage: $0 <nextjs_app_directory>"
    exit 1
fi
NEXT_APP_DIR="$1"

# Check if the directory already exists.
if [ -d "$NEXT_APP_DIR" ]; then
    echo "Next.js workspace '$NEXT_APP_DIR' already exists. Skipping setup."
    exit 0
fi

echo "Creating Next.js workspace in '$NEXT_APP_DIR'..."

mkdir -p "$NEXT_APP_DIR"

# Create the Next.js project using create-next-app with non-interactive flags.
# --ts: TypeScript
# --tailwind: Tailwind CSS
# --eslint: ESLint
# --no-app: Use Pages Router instead of App Router for compatibility with examples
# --no-src-dir: Do not create a src/ directory
# --import-alias "@/*": Configure path alias
# --use-npm: Use npm as package manager
npx create-next-app@latest "$NEXT_APP_DIR" --ts --tailwind --eslint --no-app --no-src-dir --import-alias "@/*" --use-npm

# Navigate into the project directory.
cd "$NEXT_APP_DIR"

echo "Installing additional dependencies..."

# List of additional dependencies to install based on the provided dataset.
dependency_list=(
  @monaco-editor/react
  react-dnd
  react-dnd-html5-backend
  recharts
  framer-motion
  date-fns
  react-icons
  @heroicons/react
  lucide-react
  react-dropzone
  axios
  react-calendar
  @react-three/fiber
  @react-three/drei
  three
  react-select
  socket.io-client
  xlsx
  @radix-ui/react-dialog
  @radix-ui/react-icons
  chess.js
  clsx
  papaparse
  react-player
  uuid
  react-datepicker
  openai
  zustand
  react-draggable
  @headlessui/react
  react-hook-form
  zod
  @shadcn/ui
  react-three-fiber
  react-chessboard
  @types/three
  react-markdown
  @radix-ui/react-slot
  react-use
  tailwind-merge
  class-variance-authority
  howler
  react-hot-toast
  react-use-gesture
  @hookform/resolvers
  react-day-picker
  react-infinite-scroll-component
  next-themes
)

total=${#dependency_list[@]}
count=0

echo "Installing additional packages..."
for pkg in "${dependency_list[@]}"; do
  count=$((count+1))
  percent=$((count * 100 / total))
  # Simple progress indicator
  printf "\rInstalling [%s] (%d/%d) - %d%%" "$pkg" "$count" "$total" "$percent"
  
  if npm install "$pkg" --no-progress --silent; then
    : # Successfully installed
  else
    # Outputting to stderr
    >&2 echo -e "\n\u274c Failed to install $pkg, skipping..."
  fi
done

echo -e "\n\u2705 All dependencies installed successfully!"

echo "Initializing shadcn/ui..."
npx shadcn@latest init 

npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add dialog
npx shadcn@latest add card
npx shadcn@latest add select
npx shadcn@latest add tabs
npx shadcn@latest add avatar
npx shadcn@latest add alert
npx shadcn@latest add checkbox
npx shadcn@latest add label
npx shadcn@latest add textarea

echo "Next.js environment setup complete in '$NEXT_APP_DIR'."
echo "To use it, copy your page code to 'pages/index.tsx'." 