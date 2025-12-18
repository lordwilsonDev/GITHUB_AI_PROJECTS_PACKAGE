

# ============================================
# CLI INTERFACE
# ============================================

def cmd_run(args):
    sequence_path = Path(args.sequence)
    if not sequence_path.exists():
        sequence_path = SEQUENCES_DIR / args.sequence
        if not sequence_path.exists():
            sequence_path = SEQUENCES_DIR / f"{args.sequence}.yaml"
    
    if not sequence_path.exists():
        logger.error(f"Sequence not found: {args.sequence}")
        sys.exit(1)
    
    sequence = Sequence.from_yaml(sequence_path)
    executor = SequenceExecutor(sequence, resume=args.resume)
    result = executor.run()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
    
    sys.exit(0 if result['status'] == 'success' else 1)


def cmd_list(args):
    print("\n🔮 Available Sequences:")
    print("=" * 50)
    
    for seq_file in SEQUENCES_DIR.glob("*.yaml"):
        try:
            seq = Sequence.from_yaml(seq_file)
            print(f"\n📋 {seq.name}")
            print(f"   {seq.description}")
            print(f"   Steps: {len(seq.steps)}")
        except Exception as e:
            print(f"\n⚠️  {seq_file.name} (error: {e})")
    
    print("\n" + "=" * 50)
    print("\n🔧 Registered Systems:")
    for name in SYSTEM_REGISTRY:
        print(f"   - {name}")
    print()


def cmd_init(args):
    template = {
        'name': args.name, 'description': f'{args.name} sequence', 'version': '1.0',
        'variables': {'home': str(HOME)},
        'steps': [
            {'name': 'example-shell', 'type': 'shell', 'config': {'command': 'echo "Hello from Universal Adapter"'}}
        ]
    }
    output_path = SEQUENCES_DIR / f"{args.name}.yaml"
    with open(output_path, 'w') as f:
        yaml.dump(template, f, default_flow_style=False, sort_keys=False)
    print(f"✅ Created sequence template: {output_path}")


def cmd_status(args):
    state = ExecutionState.load(args.sequence)
    if not state:
        print(f"No state found for sequence: {args.sequence}")
        sys.exit(1)
    
    print(f"\n📊 Sequence Status: {state.sequence_name}")
    print("=" * 50)
    print(f"Started: {state.started_at}")
    print(f"Updated: {state.updated_at}")
    print(f"Current Step: {state.current_step + 1}")
    print(f"\nStep Results:")
    
    for name, result in state.step_results.items():
        status = result['status']
        emoji = '✅' if status == 'success' else '❌' if status == 'failed' else '⏭'
        print(f"  {emoji} {name}: {status}")
    print()


def cmd_systems(args):
    print("\n🔧 Registered Systems:")
    print("=" * 50)
    for name, config in SYSTEM_REGISTRY.items():
        print(f"\n📦 {name}")
        print(f"   Type: {config['type']}")
        print(f"   Config: {config['config']}")
    print()


def main():
    parser = argparse.ArgumentParser(description='🔮 Universal Adapter - Meta-Orchestration for Cognitive Systems')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    run_parser = subparsers.add_parser('run', help='Run a sequence')
    run_parser.add_argument('sequence', help='Path to sequence YAML or sequence name')
    run_parser.add_argument('--resume', action='store_true', help='Resume from last state')
    run_parser.add_argument('--output', '-o', help='Output results to JSON file')
    run_parser.set_defaults(func=cmd_run)
    
    list_parser = subparsers.add_parser('list', help='List available sequences')
    list_parser.set_defaults(func=cmd_list)
    
    init_parser = subparsers.add_parser('init', help='Create new sequence from template')
    init_parser.add_argument('name', help='Name for the new sequence')
    init_parser.set_defaults(func=cmd_init)
    
    status_parser = subparsers.add_parser('status', help='Show sequence status')
    status_parser.add_argument('sequence', help='Sequence name')
    status_parser.set_defaults(func=cmd_status)
    
    systems_parser = subparsers.add_parser('systems', help='List system registry')
    systems_parser.set_defaults(func=cmd_systems)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == '__main__':
    main()
