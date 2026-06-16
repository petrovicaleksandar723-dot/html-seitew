#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OrbPickup.generated.h"

class USphereComponent;
class UStaticMeshComponent;
class UPointLightComponent;
class UMaterialInstanceDynamic;

/**
 * A glowing collectible orb. Uses an engine basic-shape sphere + a bright
 * PointLight so Lumen bounces colored GI around the arena (the cinematic look).
 * (ue-actor-component-architecture + ue-physics-collision + ue-materials-rendering)
 */
UCLASS()
class LUMENARENA_API AOrbPickup : public AActor
{
	GENERATED_BODY()

public:
	AOrbPickup();

	/** Tint the orb (mesh emissive-ish base color + light color). */
	void SetOrbColor(const FLinearColor& InColor);

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& Sweep);

protected:
	UPROPERTY(VisibleAnywhere, Category = "Orb")
	TObjectPtr<USphereComponent> Trigger;

	UPROPERTY(VisibleAnywhere, Category = "Orb")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(VisibleAnywhere, Category = "Orb")
	TObjectPtr<UPointLightComponent> Glow;

	UPROPERTY(EditAnywhere, Category = "Orb")
	float SpinSpeed = 90.f;

	UPROPERTY(EditAnywhere, Category = "Orb")
	float BobHeight = 35.f;

	UPROPERTY(EditAnywhere, Category = "Orb")
	float BobSpeed = 2.f;

private:
	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> DynMat;

	FLinearColor OrbColor = FLinearColor(0.2f, 0.7f, 1.0f);
	float BaseZ = 0.f;
	float Phase = 0.f;
	bool bCollected = false;
};
