#include "ArenaHUD.h"
#include "ArenaGameState.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "GameFramework/GameStateBase.h"

void AArenaHUD::DrawHUD()
{
	Super::DrawHUD();

	if (!Canvas)
	{
		return;
	}

	const AArenaGameState* GS = GetWorld() ? GetWorld()->GetGameState<AArenaGameState>() : nullptr;
	if (!GS)
	{
		return;
	}

	UFont* Font = GEngine ? GEngine->GetLargeFont() : nullptr;
	if (!Font)
	{
		return;
	}

	const float Pad = 48.f;

	// Score
	{
		const FString Score = FString::Printf(TEXT("ORBS  %d / %d"), GS->Collected, GS->Total);
		FCanvasTextItem Item(FVector2D(Pad, Pad), FText::FromString(Score), Font, FLinearColor(0.6f, 0.85f, 1.0f));
		Item.Scale = FVector2D(1.6f, 1.6f);
		Item.EnableShadow(FLinearColor::Black);
		Canvas->DrawItem(Item);
	}

	// Timer
	{
		const FString Timer = FString::Printf(TEXT("%.1f s"), GS->GetElapsedSeconds());
		FCanvasTextItem Item(FVector2D(Canvas->SizeX - 220.f, Pad), FText::FromString(Timer), Font, FLinearColor(0.85f, 0.75f, 1.0f));
		Item.Scale = FVector2D(1.4f, 1.4f);
		Item.EnableShadow(FLinearColor::Black);
		Canvas->DrawItem(Item);
	}

	// Objective / win banner
	{
		const FString Msg = GS->bFinished
			? FString::Printf(TEXT("ALLE ORBS GESAMMELT  —  %.1f s"), GS->GetElapsedSeconds())
			: TEXT("Sammle alle leuchtenden Orbs");
		const FLinearColor Col = GS->bFinished ? FLinearColor(0.4f, 1.0f, 0.6f) : FLinearColor(1.f, 1.f, 1.f, 0.7f);
		FCanvasTextItem Item(FVector2D(Pad, Canvas->SizeY - 80.f), FText::FromString(Msg), Font, Col);
		Item.Scale = FVector2D(1.2f, 1.2f);
		Item.EnableShadow(FLinearColor::Black);
		Canvas->DrawItem(Item);
	}
}
