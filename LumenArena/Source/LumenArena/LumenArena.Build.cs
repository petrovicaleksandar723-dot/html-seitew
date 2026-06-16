using UnrealBuildTool;

public class LumenArena : ModuleRules
{
	public LumenArena(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput"
		});

		// IWYU-friendly: keep private deps explicit when added.
	}
}
