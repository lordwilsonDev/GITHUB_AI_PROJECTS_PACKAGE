#!/bin/bash
# Setup Universal Adapter

echo "🔮 Setting up Universal Adapter..."

# Add alias to .zshrc if not already present
if ! grep -q "alias ua=" ~/.zshrc; then
    echo "" >> ~/.zshrc
    echo "# Universal Adapter" >> ~/.zshrc
    echo "alias ua='$HOME/universal-adapter/ua'" >> ~/.zshrc
    echo "✅ Added 'ua' alias to ~/.zshrc"
else
    echo "✅ Alias already exists"
fi

# Make scripts executable
chmod +x "$HOME/universal-adapter/ua"
chmod +x "$HOME/universal-adapter/universal_adapter.py"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Run 'source ~/.zshrc' or open a new terminal, then use:"
echo "  ua list        - See available sequences"
echo "  ua health      - Check system health"
echo "  ua mega        - Run the mega pipeline"
echo ""
